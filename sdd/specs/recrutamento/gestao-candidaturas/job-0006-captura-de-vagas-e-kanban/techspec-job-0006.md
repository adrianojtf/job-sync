# Especificação Técnica

## Resumo Executivo

Esta Tech Spec cobre dois blocos definidos em `prd-job-0006.md`: (1) uma extensão de navegador Chrome (Manifest V3) que captura o texto de uma página e o envia para a aplicação, e (2) um Kanban de candidaturas dentro do app Streamlit existente. O ponto técnico central é que o Streamlit não expõe uma API HTTP própria para receber chamadas externas da extensão — a solução introduz um pequeno servidor HTTP local (FastAPI, rodando em processo separado na mesma máquina, porta `8502`) que compartilha o mesmo SQLite criado na Fase 0 (`job-0004`). A extensão autentica via um token de captura gerado uma vez pelo usuário dentro do Streamlit e colado nas opções da extensão — não há novo sistema de login.

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `Vaga` (novo, `domain/vaga.py`): entidade com `id`, `perfil_identificador`, `texto_descricao`, `url_origem`, `data_captura`.
- `Candidatura` (novo, `domain/candidatura.py`): entidade com `id`, `perfil_identificador`, `vaga_id`, `curriculo_salvo_id`, `empresa`, `cargo`, `status: StatusCandidatura`, `data_aplicacao`, `historico_status: tuple[MudancaStatus, ...]`.
- `StatusCandidatura` (novo, enum em `domain/candidatura.py`): `APLICADO`, `ENTREVISTA`, `OFERTA`, `REJEITADO`.
- `RepositorioVagaPort` / `RepositorioCandidaturaPort` (novos, `application/ports/`): interfaces de persistência, seguindo o padrão de `RepositorioPerfilPort` da Fase 0.
- `CapturarVaga`, `ListarVagasCapturadas`, `CriarCandidatura`, `MoverCandidatura`, `ListarCandidaturasPorStatus` (novos use cases, `application/use_cases/`).
- `TokenCaptura` (novo, `domain/token_captura.py`): value object simples associando um token opaco a um `perfil_identificador`, gerado sob demanda pelo usuário.
- `RepositorioSqlite` (existente, Fase 0, estendido): ganha tabelas `vaga`, `candidatura`, `mudanca_status` e `token_captura`.
- `ServidorCaptura` (novo, `infrastructure/api/servidor_captura.py`): app FastAPI rodando em processo separado, expõe `POST /api/vagas/capturar`, único ponto de entrada externo do sistema.
- `extensao-chrome/` (novo diretório na raiz do projeto): manifest v3, `content.js` (extrai texto da página), `background.js` (envia para o servidor de captura), `popup.html` (onde o usuário cola o token de captura).
- `ui/app_streamlit.py` (modificado): ganha tela de geração/exibição do token de captura, lista de vagas capturadas, e o quadro Kanban.

Fluxo de dados — captura:
1. Usuário clica no botão da extensão → `content.js` extrai `document.body.innerText` (heurística simples) e a URL atual.
2. `background.js` faz `POST http://localhost:8502/api/vagas/capturar` com `{texto, url}` e header `Authorization: Bearer <token>`.
3. `ServidorCaptura` resolve o `perfil_identificador` a partir do token via `TokenCaptura`, chama `CapturarVaga.executar()`, que persiste a `Vaga` via `RepositorioVagaPort`.
4. Streamlit, ao ser recarregado pelo usuário, lista as vagas capturadas via `ListarVagasCapturadas.executar(perfil_identificador)`.

Fluxo de dados — Kanban:
1. Usuário cria candidatura a partir de uma vaga (capturada ou colada) + currículo salvo (Fase 0) → `CriarCandidatura.executar()`.
2. UI renderiza quatro colunas chamando `ListarCandidaturasPorStatus.executar(perfil_identificador)` (agrupado por status).
3. Ao mover um cartão, UI chama `MoverCandidatura.executar(candidatura_id, novo_status)`.

## Design de Implementação

### Interfaces Principais

```python
class RepositorioVagaPort(ABC):
    @abstractmethod
    def salvar(self, vaga: Vaga) -> Vaga: ...

    @abstractmethod
    def listar_nao_convertidas(self, perfil_identificador: str) -> tuple[Vaga, ...]: ...


class RepositorioCandidaturaPort(ABC):
    @abstractmethod
    def salvar(self, candidatura: Candidatura) -> Candidatura: ...

    @abstractmethod
    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]: ...

    @abstractmethod
    def atualizar_status(self, candidatura_id: str, novo_status: StatusCandidatura) -> Candidatura: ...
```

Endpoint FastAPI (único endpoint externo do sistema):

```python
@app.post("/api/vagas/capturar")
def capturar_vaga(payload: CapturaVagaRequest, authorization: str = Header(...)) -> CapturaVagaResponse:
    ...
```

### Modelos de Dados

```python
@dataclass(frozen=True)
class Vaga:
    id: str
    perfil_identificador: str
    texto_descricao: str
    url_origem: str
    data_captura: datetime

class StatusCandidatura(Enum):
    APLICADO = auto()
    ENTREVISTA = auto()
    OFERTA = auto()
    REJEITADO = auto()

@dataclass(frozen=True)
class Candidatura:
    id: str
    perfil_identificador: str
    vaga_id: str
    curriculo_salvo_id: str
    empresa: str
    cargo: str
    status: StatusCandidatura
    data_aplicacao: datetime
```

Esquema SQLite adicional (estende o banco da Fase 0):

```sql
CREATE TABLE token_captura (
    token TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador)
);

CREATE TABLE vaga (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    texto_descricao TEXT NOT NULL,
    url_origem TEXT,
    data_captura TEXT NOT NULL,
    convertida_em_candidatura INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE candidatura (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    vaga_id TEXT REFERENCES vaga(id),
    curriculo_salvo_id TEXT REFERENCES curriculo_salvo(id),
    empresa TEXT NOT NULL,
    cargo TEXT NOT NULL,
    status TEXT NOT NULL,
    data_aplicacao TEXT NOT NULL
);
```

### Endpoints de API

- `POST /api/vagas/capturar` — único endpoint externo. Corpo: `{"texto": str, "url": str}`. Header: `Authorization: Bearer <token_captura>`. Retorna `201` com o id da vaga criada, ou `401` se o token for inválido.

## Pontos de Integração

- `infrastructure/persistence/repositorio_sqlite.py` (Fase 0): estendido para implementar também `RepositorioVagaPort` e `RepositorioCandidaturaPort`, reaproveitando a mesma conexão/arquivo `storage/job_sync.db`.
- Extensão Chrome ↔ `ServidorCaptura`: único ponto de rede novo no projeto; roda em `localhost`, não exposto externamente — sem necessidade de HTTPS/TLS para este escopo local.
- `ServidorCaptura` precisa ser iniciado junto com o Streamlit (dois processos); documentar no README-macos.md o novo passo de execução (`uvicorn infrastructure.api.servidor_captura:app --port 8502`).

## Abordagem de Testes

### Testes Unidade

- `CapturarVaga`, `CriarCandidatura`, `MoverCandidatura`: usando fakes de `RepositorioVagaPort`/`RepositorioCandidaturaPort`, seguindo o padrão já usado nos testes da Fase 0.
- Validação de transição de status: garantir que `MoverCandidatura` aceita qualquer transição entre as quatro colunas (sem máquina de estados restritiva, já que o PRD não define ordem obrigatória).
- `TokenCaptura`: geração de token único e resolução correta de perfil a partir do token.

### Testes de Serviço

- `ServidorCaptura`: teste de integração usando `TestClient` do FastAPI, cobrindo captura com token válido (201), token inválido (401) e payload sem texto (422).
- `RepositorioSqlite` estendido: teste de integração cobrindo persistência e listagem de vagas/candidaturas isoladas por perfil (mesma abordagem de isolamento validada na Fase 0).

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Entidades de domínio (`Vaga`, `Candidatura`, `StatusCandidatura`, `TokenCaptura`) — sem dependências novas.
2. Portas + extensão do `RepositorioSqlite` com as novas tabelas, com testes de integração.
3. Use cases de vaga e candidatura, com testes unitários usando fakes.
4. `ServidorCaptura` (FastAPI) com o endpoint único de captura, testado com `TestClient`.
5. Extensão Chrome (manifest, content script, background script, popup de configuração do token) — só faz sentido depois do servidor estar funcional e testável via `curl`.
6. Kanban na UI Streamlit, consumindo os use cases de candidatura.
7. Validação manual: capturar uma vaga real de uma página, confirmar que aparece na lista do Streamlit, criar candidatura e mover entre colunas.

### Dependências Técnicas

- Nova dependência: `fastapi` e `uvicorn` (adicionar a `requirements.txt`).
- Depende da Fase 0 (`job-0004`) estar implementada — reaproveita perfil, SQLite e biblioteca de currículos salvos.
- Chrome (ou navegador baseado em Chromium) para a extensão Manifest V3.

## Monitoramento e Observabilidade

- `ServidorCaptura` deve logar (INFO) cada captura recebida com sucesso (perfil + URL de origem, sem logar o texto completo), e (WARNING) tentativas com token inválido.
- Streamlit deve logar (ERROR) falhas ao persistir candidatura ou mudança de status.

## Considerações Técnicas

### Decisões Principais

- Servidor HTTP separado (FastAPI) em vez de tentar expor endpoint dentro do próprio processo Streamlit: Streamlit não foi desenhado para servir APIs externas de forma confiável: separar os processos mantém cada um simples e testável isoladamente.
- Token de captura opaco e de longa duração (não expira) em vez de OAuth/sessão completa: proporcional ao contexto de uso pessoal/portfólio já definido nas fases anteriores — evita construir um fluxo de autenticação completo para a extensão.
- Extração de texto por heurística genérica (`innerText` da página) em vez de seletores específicos por site: evita manutenção contínua de parsers que quebram a cada mudança de layout do LinkedIn/Gupy/etc., ao custo de exigir revisão manual do texto capturado (já previsto no PRD).

### Riscos Conhecidos

- Extração genérica de texto pode capturar ruído (menus, rodapé) além da descrição da vaga — mitigado pelo requisito de edição manual antes de converter em candidatura (PRD, requisito 5).
- Rodar dois processos (Streamlit + FastAPI) aumenta a complexidade operacional local — aceitável no escopo de uso pessoal, mas deve ficar documentado claramente no README.
- Token de captura sem expiração é um risco de segurança se vazar — aceitável no contexto declarado (uso pessoal/portfólio), mas deve ficar registrado como limitação conhecida.

### Conformidade com Padrões

Não há regras em `.windsurf/rules` no repositório (diretório inexistente) — nenhum desvio a documentar. Mantém a Arquitetura Hexagonal: `ServidorCaptura` e a extensão Chrome são adapters de infraestrutura, sem lógica de negócio própria além de desserializar a requisição e chamar o use case.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/gestao-candidaturas/job-0006-captura-de-vagas-e-kanban/prd-job-0006.md`
- `domain/vaga.py`, `domain/candidatura.py`, `domain/token_captura.py` (novos)
- `application/ports/repositorio_vaga_port.py`, `application/ports/repositorio_candidatura_port.py` (novos)
- `application/use_cases/capturar_vaga.py`, `criar_candidatura.py`, `mover_candidatura.py`, `listar_candidaturas_por_status.py`, `listar_vagas_capturadas.py` (novos)
- `infrastructure/persistence/repositorio_sqlite.py` (modificado — Fase 0)
- `infrastructure/api/servidor_captura.py` (novo)
- `extensao-chrome/manifest.json`, `content.js`, `background.js`, `popup.html` (novos)
- `ui/app_streamlit.py` (modificado)
- `requirements.txt` (modificado — `fastapi`, `uvicorn`)

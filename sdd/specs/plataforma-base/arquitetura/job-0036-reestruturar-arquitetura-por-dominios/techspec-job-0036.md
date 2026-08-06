# Tech Spec — Reestruturar o projeto para a arquitetura por domínios

- **Código**: `job-0036`
- **Módulo**: `plataforma-base`
- **Subsistema**: `arquitetura`
- **Status**: Rascunho
- **Baseado em**: [prd-job-0036.md](prd-job-0036.md)

## Resumo Executivo

A estrutura atual do `src/` — dividida em `application/`, `domain/`, `infrastructure/`, `ui/` e `tests/` — será reorganizada em um layout por domínios em `src/jobsync/`, alinhado às regras de design do projeto (`code-design-standards.md`, `AGENTS.md`). Cada domínio passará a conter suas próprias camadas `domain/`, `service_layer/` e `adapters/`, com `entrypoints/` centralizando `streamlit_app.py` e `servidor_captura.py`, e `shared_kernel/` abrigando conceitos transversais. A refatoração é pura: não muda contratos, comportamento, endpoints FastAPI nem a interface do Streamlit. A entrega será incremental por domínio, validada pela suíte de testes existente e complementada por contratos `import-linter` para prevenir dependências proibidas e ciclos.

## Arquitetura do Sistema

### Visão Geral dos Componentes

| Componente (novo) | Responsabilidade |
| --- | --- |
| `src/jobsync/curriculo/` | Entidades do currículo, ajuste de texto, geração de PDF, carta de apresentação e sugestões ATS. |
| `src/jobsync/curriculo_salvo/` | Agregado `CurriculoSalvo` e casos de uso de salvar/listar/remover. |
| `src/jobsync/vaga/` | `Vaga`, `AnaliseVaga`, repositório e análise de descrição. |
| `src/jobsync/vaga_externa/` | Buscadores de vagas externas, extração de texto de páginas, descoberta e candidatura externa. |
| `src/jobsync/perfil/` | Perfil do usuário, autenticação e identificação. |
| `src/jobsync/perfil_estruturado/` | Extração e montagem de perfil estruturado a partir de PDF. |
| `src/jobsync/candidatura/` | Candidatura, mudança de status, repositório. |
| `src/jobsync/ats_score/` | Cálculo de score ATS. |
| `src/jobsync/token_captura/` | Tokens opacos de captura de vagas. |
| `src/jobsync/shared_kernel/` | Value Objects e adapters usados por mais de um domínio. |
| `src/jobsync/entrypoints/` | `streamlit_app.py` (UI) e `servidor_captura.py` (API FastAPI). |
| `src/jobsync/tests/` | Espelha `src/jobsync/` por domínio. |
| `import-linter` | Configurado em `pyproject.toml` (ou `setup.cfg`) para garantir isolamento. |

### Relacionamentos e fluxo de dados

1. `entrypoints` compõem os adapters concretos e invocam os `Services` da camada `service_layer`.
2. Cada `Service` orquestra entidades do próprio `domain` e ports locais; quando precisa de dados de outro domínio, recebe o repositório/port por injeção.
3. `adapters` implementam ports (repositórios SQLite, clients Groq, buscadores, geradores PDF).
4. Domínios referenciam outros apenas por ID, exceto por Value Objects compartilhados em `shared_kernel`.

## Design de Implementação

### Interfaces principais

```python
# jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/service.py
@dataclass
class AdaptarCurriculoParaVaga:
    _extrator: ExtratorCurriculoPort
    _analisador_vaga: JobDescriptionAnalyzerPort
    _ajustador_texto: AjustadorTextoPort
    _gerador_pdf: GeradorPdfPort

    def executar(
        self,
        input_dto: AdaptarCurriculoParaVagaInputDto,
    ) -> AdaptarCurriculoParaVagaOutputDto: ...
```

```python
# jobsync/curriculo/domain/ajustador_texto_port.py
class AjustadorTextoPort(Protocol):
    def ajustar_secao(
        self,
        secao: SecaoCurriculo,
        descricao_vaga: str,
        idioma_alvo: IdiomaAlvo,
        analise_vaga: AnaliseVaga,
    ) -> SecaoCurriculo: ...
```

```python
# jobsync/curriculo/adapters/ajustador_texto_client.py
class AjustadorTextoClient(AjustadorTextoPort):
    def __init__(self, cliente_groq: ClienteGroq) -> None: ...
```

### Modelos de dados

Os modelos de domínio **não sofrem alteração semântica**. Apenas mudam de pacote:

- `jobsync.curriculo.domain.Curriculo`, `SecaoCurriculo`, `TipoSecao`
- `jobsync.vaga.domain.Vaga`, `AnaliseVaga`, `RequisitoTecnico`
- `jobsync.perfil_estruturado.domain.PerfilEstruturado`, `ExperienciaProfissional`, etc.
- `jobsync.candidatura.domain.Candidatura`, `StatusCandidatura`, `MudancaStatus`
- `jobsync.shared_kernel.domain.NomeArquivo`

### Endpoints de API

Nenhum endpoint é alterado. `POST /api/vagas/capturar` continua implementado em `entrypoints/servidor_captura.py`. Todos os imports internos passam a partir do novo pacote `jobsync`.

## Pontos de Integração

- **Groq API**: clients em cada domínio (`ajustador_texto_client.py`, `job_description_analyzer_client.py`, etc.) continuam atrás de ports.
- **Fontes externas de vagas**: Adzuna, Arbeitnow, RemoteOk, WeWorkRemotely, Google CSE permanecem em `vaga_externa/adapters/`.
- **SQLite**: repositories `Impl` continuam em `candidatura/adapters/`, `perfil/adapters/`, `vaga/adapters/`, etc.
- **Extensão Chrome**: o servidor de captura autentica via `token_captura` e chama `vaga`.

## Abordagem de Testes

### Testes de unidade

- Espelhar `src/jobsync/tests/` de acordo com a nova estrutura: `jobsync/tests/curriculo/`, `jobsync/tests/candidatura/` etc.
- Cada domínio migrado leva seus testes no mesmo incremento.
- Manter fakes e stubs existentes, ajustando caminhos de import.

### Testes de arquitetura

Adicionar `import-linter` com contratos para garantir:

- `domain` de um domínio não importa `adapters`, `service_layer` de outro domínio, nem `infrastructure`.
- `service_layer` importa `domain` e ports, mas não adapters concretos.
- `adapters` importa ports de `domain` e bibliotecas externas.
- `entrypoints` importa `service_layer` e `adapters`, nunca `domain` diretamente (exceto para expor enums/Value Objects já previstos em `shared_kernel`).
- Ausência de ciclos de importação entre domínios.

## Sequenciamento de Desenvolvimento

### Ordem de construção

1. **Pré-migração**: criar `src/jobsync/`, ajustar `pytest.ini`, `PYTHONPATH` e `requirements.txt` (`import-linter`).
2. **Shared kernel**: `nome_arquivo`, `localizacao` e, se confirmado, `AnaliseVaga`/`ResultadoAtsScore` para reduzir dependências cruzadas.
3. **Domínios folha**: `ats_score`, `token_captura`.
4. **Domínios com persistência simples**: `perfil`, `curriculo_salvo`, `vaga`.
5. **Domínios de negócio**: `candidatura`, `perfil_estruturado`.
6. **Domínio core**: `curriculo` (adaptação, PDF, carta, ATS) e `vaga_externa`.
7. **Entrypoints**: mover e reconfigurar `streamlit_app.py` e `servidor_captura.py`.
8. **Import-linter e testes de arquitetura**.
9. **Limpeza**: remover os diretórios antigos (`application`, `domain`, `infrastructure`, `ui`, `tests` legacy) após validação.

Cada incremento deve manter `pytest` passando, permitindo `git bisect` e rollback.

### Dependências técnicas

- `import-linter` adicionado a `requirements.txt`.
- `pytest` já configurado.
- Nenhuma mudança de infraestrutura externa (DB, APIs).

## Monitoramento e Observabilidade

- Manter logs existentes.
- Adicionar execução do `import-linter` na checagem de CI/PR (`lint-imports`).
- Atualizar `README.md` com a nova estrutura de pastas.

## Considerações Técnicas

### Decisões principais

- **Pacote raiz `jobsync`**: evita hífen inválido em nomes de pacote Python e reflete a linguagem ubíqua. `src/` continua no `pythonpath`.
- **Migração incremental**: reduz risco de conflitos e permite entrega parcial. `__init__.py` de compatibilidade podem reexportar símbolos durante a transição.
- **Renomear `use_case.py` → `service.py` e manter `executar`**: alinha às regras de `service_layer`.
- **Sufixos `Impl`/`Client`**: repositórios e clients externos ganham nomes consistentes sem perder identidade (ex.: `AjustadorTextoClient` encapsula o Groq internamente).
- **`shared_kernel`**: abriga `NomeArquivo` e `CatalogoLocalizacao` (usados em mais de um domínio). `AnaliseVaga`/`ResultadoAtsScore` serão reavaliados durante a migração: se realmente compartilhados, migram para `shared_kernel/domain`; caso contrário, os ports passarão a receber apenas primitivos/IDs sem alterar o contrato dos entrypoints.

### Riscos conhecidos

- **Imports quebrados**: ajustar `PYTHONPATH` e todos os imports absolutos. Mitigação: passos de busca/replace validados por testes a cada PR.
- **Ciclos de importação**: reorganização de `__init__.py` pode criar ciclos. Mitigação: importações `TYPE_CHECKING` e revisão pelo `import-linter`.
- **Testes quebrados por paths**: `pytest.ini` precisará ser atualizado. Mitigação: rodar `pytest` a cada domínio migrado.
- **Comportamento inadvertido**: renomear arquivos pode quebrar import dinâmico. Mitigação: manter `__init__.py` com reexports.

### Conformidade com padrões

- `code-design-standards.md` — estrutura por domínios, DTOs, Services, método `executar`, separação de camadas.
- `back-end-general-rules.md` — rotas FastAPI mantêm contrato; nenhum endpoint alterado.
- `general-rules.md` e `AGENTS.md` — Clean Code, DRY, KISS, DDD, Hexagonal, TDD.
- `testing-rules.md` — testes espelham estrutura; adição de testes de arquitetura.

### Arquivos relevantes e dependentes

- `src/application/use_cases/**`
- `src/domain/**`
- `src/infrastructure/**`
- `src/ui/app_streamlit.py`
- `src/infrastructure/api/servidor_captura.py`
- `src/tests/**`
- `pytest.ini`
- `requirements.txt`
- `README.md`

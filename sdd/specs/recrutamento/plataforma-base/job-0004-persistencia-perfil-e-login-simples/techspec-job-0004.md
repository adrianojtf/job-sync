# Especificação Técnica

## Resumo Executivo

Esta Tech Spec descreve a implementação da camada de persistência e do login simples definidos no PRD `prd-job-0004.md`. A abordagem introduz duas novas entidades de domínio (`Perfil` e `CurriculoSalvo`), duas portas de aplicação (`RepositorioPerfilPort`, `RepositorioCurriculoSalvoPort`) e um adapter de infraestrutura em SQLite, seguindo o mesmo padrão de Ports and Adapters já usado pelo `AdaptarCurriculoParaVaga`. O Streamlit ganha uma tela de entrada (identificador) e uma biblioteca de currículos, ambas na camada `ui/`, sem alterar o fluxo de adaptação já existente — ele passa a poder receber um currículo já salvo como entrada alternativa ao upload.

SQLite foi escolhido por não exigir infraestrutura externa (compatível com o modelo de execução local via `streamlit run`) e por ser suficiente para o volume de dados esperado (uso pessoal, 2-4 perfis, 10 currículos cada).

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `Perfil` (novo, `domain/perfil.py`): entidade de domínio representando um usuário identificado apenas por `identificador` (string única).
- `CurriculoSalvo` (novo, `domain/curriculo_salvo.py`): entidade representando um PDF salvo — `id`, `perfil_identificador`, `nome_referencia`, `pdf_bytes`, `data_upload`. Distinta de `Curriculo` (domain existente), que representa o currículo já parseado/estruturado.
- `RepositorioPerfilPort` (novo, `application/ports/repositorio_perfil_port.py`): interface para buscar/criar perfil por identificador.
- `RepositorioCurriculoSalvoPort` (novo, `application/ports/repositorio_curriculo_salvo_port.py`): interface para salvar, listar, remover e obter currículos salvos de um perfil.
- `EntrarOuCriarPerfil` (novo use case, `application/use_cases/entrar_ou_criar_perfil.py`): recebe um identificador, retorna o `Perfil` existente ou cria um novo.
- `SalvarCurriculo` / `ListarCurriculosSalvos` / `RemoverCurriculoSalvo` (novos use cases, `application/use_cases/`): operações da biblioteca de currículos, aplicando a regra de limite de 10 por perfil.
- `RepositorioSqlite` (novo, `infrastructure/persistence/repositorio_sqlite.py`): implementa ambas as portas usando `sqlite3` da stdlib, arquivo único em `storage/job_sync.db`.
- `ui/app_streamlit.py` (existente, modificado): ganha tela de entrada por identificador (guarda `perfil_identificador` em `st.session_state`) e uma seção de biblioteca de currículos antes do formulário de adaptação já existente.

Fluxo de dados proposto:
1. Usuário informa identificador → `EntrarOuCriarPerfil.executar()` → `Perfil` fica em `st.session_state`.
2. UI lista currículos salvos via `ListarCurriculosSalvos.executar(perfil.identificador)`.
3. Usuário faz upload novo (`SalvarCurriculo`) ou seleciona um existente da lista.
4. O `pdf_bytes` selecionado (novo ou salvo) segue para `AdaptarCurriculoParaVaga.executar()` sem nenhuma alteração nesse caso de uso.

## Design de Implementação

### Interfaces Principais

```python
class RepositorioPerfilPort(ABC):
    @abstractmethod
    def buscar_por_identificador(self, identificador: str) -> Optional[Perfil]: ...

    @abstractmethod
    def criar(self, identificador: str) -> Perfil: ...


class RepositorioCurriculoSalvoPort(ABC):
    @abstractmethod
    def salvar(self, curriculo: CurriculoSalvo) -> CurriculoSalvo: ...

    @abstractmethod
    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]: ...

    @abstractmethod
    def remover(self, curriculo_id: str, perfil_identificador: str) -> None: ...

    @abstractmethod
    def contar_por_perfil(self, perfil_identificador: str) -> int: ...
```

### Modelos de Dados

```python
@dataclass(frozen=True)
class Perfil:
    identificador: str  # chave natural, ex: "matheus"

@dataclass(frozen=True)
class CurriculoSalvo:
    id: str  # uuid4
    perfil_identificador: str
    nome_referencia: str
    pdf_bytes: bytes
    data_upload: datetime
```

Esquema SQLite:

```sql
CREATE TABLE perfil (
    identificador TEXT PRIMARY KEY
);

CREATE TABLE curriculo_salvo (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    nome_referencia TEXT NOT NULL,
    pdf_bytes BLOB NOT NULL,
    data_upload TEXT NOT NULL
);
```

### Endpoints de API

Não aplicável — a aplicação continua sendo um app Streamlit monolítico sem API HTTP separada.

## Pontos de Integração

- Nenhuma integração externa nova. SQLite é embutido (`sqlite3` da stdlib do Python), sem dependência adicional em `requirements.txt`.

## Abordagem de Testes

### Testes Unidade

- `Perfil` e `CurriculoSalvo`: validação de invariantes (identificador não vazio, nome_referencia não vazio).
- `EntrarOuCriarPerfil`: cenário de perfil novo vs. perfil existente, usando um fake de `RepositorioPerfilPort` (seguindo o padrão de dublês já usado em `tests/application/test_adaptar_curriculo_para_vaga.py`).
- `SalvarCurriculo`: cenário de sucesso e cenário de bloqueio ao atingir 10 currículos, usando fake de `RepositorioCurriculoSalvoPort`.
- `RemoverCurriculoSalvo`: remoção de currículo pertencente ao perfil; tentativa de remover currículo de outro perfil deve falhar.

### Testes de Serviço

- `RepositorioSqlite`: teste de integração usando um arquivo SQLite temporário (`tempfile`), cobrindo criação de perfil, salvar/listar/remover currículo, e isolamento entre perfis diferentes (perfil A não vê currículos do perfil B).

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Entidades de domínio `Perfil` e `CurriculoSalvo` (sem dependências).
2. Portas `RepositorioPerfilPort` e `RepositorioCurriculoSalvoPort`.
3. Adapter `RepositorioSqlite` implementando ambas as portas, com testes de integração.
4. Use cases (`EntrarOuCriarPerfil`, `SalvarCurriculo`, `ListarCurriculosSalvos`, `RemoverCurriculoSalvo`), com testes unitários usando fakes.
5. Integração na UI Streamlit: tela de entrada + biblioteca de currículos + seleção de currículo salvo alimentando o fluxo existente de adaptação.
6. Validação manual: fechar e reabrir a aplicação, confirmar que os dados persistem no arquivo `storage/job_sync.db`.

### Dependências Técnicas

- Nenhuma biblioteca nova necessária (`sqlite3` é stdlib).
- Depende da estrutura de diretório `storage/` já existente no projeto (usada hoje para PDFs gerados).

## Monitoramento e Observabilidade

- Registrar em log (nível INFO) criação de novo perfil e salvamento/remoção de currículo, incluindo o identificador do perfil (sem logar o conteúdo do PDF).
- Falhas de acesso ao SQLite (arquivo bloqueado, corrompido) devem ser logadas em nível ERROR com mensagem clara para o usuário na UI.

## Considerações Técnicas

### Decisões Principais

- SQLite em vez de um banco cliente-servidor (Postgres/MySQL): elimina necessidade de infraestrutura adicional para um cenário de uso pessoal/portfólio com poucos usuários simultâneos.
- Identificador de perfil como chave natural (string), sem gerar UUID de usuário: simplifica o login sem senha, já que não há necessidade de esconder o identificador.
- `CurriculoSalvo` como entidade separada de `Curriculo`: `Curriculo` representa a estrutura já extraída/parseada (seções), enquanto `CurriculoSalvo` é o artefato bruto (PDF) na biblioteca — misturar os dois acoplaria a biblioteca de arquivos à lógica de extração por IA, que só deve rodar quando o usuário efetivamente for adaptar o currículo para uma vaga.

### Riscos Conhecidos

- Sem senha, qualquer pessoa com acesso à aplicação pode entrar com o identificador de outra pessoa e ver seus currículos — aceitável no contexto de uso pessoal/portfólio declarado no PRD, mas deve ficar documentado como limitação conhecida caso o produto evolua além disso.
- SQLite com acesso concorrente de múltiplos processos Streamlit pode gerar contenção de lock em alta concorrência — não é um risco relevante no volume de uso esperado (2-4 pessoas).

### Conformidade com Padrões

Não há regras em `.windsurf/rules` no repositório atual (diretório inexistente) — nenhum desvio a documentar. A implementação segue o padrão de Arquitetura Hexagonal já estabelecido pelo projeto (domain sem dependência de infraestrutura, portas em `application/ports`, adapters em `infrastructure/`).

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/plataforma-base/job-0004-persistencia-perfil-e-login-simples/prd-job-0004.md`
- `domain/perfil.py` (novo)
- `domain/curriculo_salvo.py` (novo)
- `application/ports/repositorio_perfil_port.py` (novo)
- `application/ports/repositorio_curriculo_salvo_port.py` (novo)
- `application/use_cases/entrar_ou_criar_perfil.py` (novo)
- `application/use_cases/salvar_curriculo.py` (novo)
- `application/use_cases/listar_curriculos_salvos.py` (novo)
- `application/use_cases/remover_curriculo_salvo.py` (novo)
- `infrastructure/persistence/repositorio_sqlite.py` (novo)
- `ui/app_streamlit.py` (modificado)
- `storage/` (diretório existente, passa a conter também `job_sync.db`)

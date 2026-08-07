# Tech Spec — Separar job-sync em backend e frontend (JOB-0012)

- **Código**: `JOB-0012`
- **Módulo**: `plataforma-base`
- **Subsistema**: `arquitetura`
- **Status**: Rascunho
- **Baseado em**: [prd-job-0012.md](prd-job-0012.md)

## Resumo Executivo

Esta Tech Spec descreve a criação do backend independente do `job-sync`. O objetivo é extrair o hexágono de domínio (`src/jobsync/...`) e expor suas operações via API HTTP FastAPI, com contrato OpenAPI/Swagger e deploy isolado. A UI Streamlit e o futuro frontend não são entregues aqui; eles serão clientes da API. A estrutura reutiliza a arquitetura hexagonal/DDD em `src/jobsync/`, seguindo `code-design-standards.md` e `back-end-general-rules.md`.

## Arquitetura do Sistema

### Visão Geral dos Componentes

| Componente | Responsabilidade |
|---|---|
| `src/jobsync/entrypoints/api/main.py` | Aplicação FastAPI, composição de routers, CORS, exception handlers. |
| `src/jobsync/entrypoints/api/routers/` | Um router por domínio (`curriculo`, `vaga`, `candidatura`, `perfil`, etc.), prefixado em `/v1/`. |
| `src/jobsync/entrypoints/api/dependencies.py` | Fornece instâncias de repositórios e services via `Depends`. |
| `src/jobsync/entrypoints/api/schemas/` | Pydantic models de request/response por domínio. |
| `<dominio>/service_layer/<funcionalidade>/service.py` | Casos de uso existentes (renomeados/mantidos), método `executar`. |
| `<dominio>/adapters/*_repository_impl.py` | Implementações de repositórios SQLite/JSON já existentes. |
| `<dominio>/adapters/*_client.py` | Clients de serviços externos (Groq, fontes de vagas). |
| `Dockerfile` | Imagem do backend isolado. |
| `.env.example` | Variáveis de ambiente do backend. |

### Relacionamentos e fluxo de dados

1. Cliente HTTP faz requisição para `/v1/<recurso>`.
2. Router recebe o request, converte schemas Pydantic em DTOs/entidades e invoca o Service via `Depends`.
3. Service orquestra `domain` e ports (repositórios, clients externos).
4. Repository/Client adapters acessam SQLite, LLM, APIs externas etc.
5. Resultado do Service é convertido para schema Pydantic e retornado com código HTTP correto.
6. Documentação OpenAPI é gerada automaticamente a partir de schemas, `response_model` e docstrings.

## Design de Implementação

### Interfaces principais

```python
# src/jobsync/entrypoints/api/main.py
from fastapi import FastAPI

app = FastAPI(
    title="Job Sync API",
    version="1.0.0",
    description="API do hexágono de domínio do job-sync",
)
```

```python
# src/jobsync/entrypoints/api/dependencies.py
from fastapi import Depends
from jobsync.entrypoints.api.composition import get_curriculo_repository


def get_adaptar_curriculo_service(
    repo: CurriculoRepository = Depends(get_curriculo_repository),
) -> AdaptarCurriculoParaVaga:
    ...
```

```python
# src/jobsync/entrypoints/api/routers/curriculo_router.py
@router.post("/{curriculo_id}/adaptacoes", status_code=200)
def adaptar_curriculo_para_vaga(...):
    ...
```

### Modelos de dados

- Pydantic `*Request` e `*Response` schemas em `src/jobsync/entrypoints/api/schemas/<dominio>.py`.
- Entidades de domínio continuam em `<dominio>/domain/model.py`, sem referência a FastAPI/Pydantic.
- DTOs de service (`InputDto`/`OutputDto`) em `<dominio>/service_layer/<funcionalidade>/dtos.py`.

### Endpoints de API (proposta v1)

A tabela abaixo reflete os domínios já existentes e os use cases que devem ser expostos. Os paths e status podem ser refinados durante a execução, mas a versão base é:

| Método | Path | Descrição |
|---|---|---|
| POST | `/v1/curriculos` | Criar currículo |
| GET | `/v1/curriculos/{id}` | Obter currículo |
| POST | `/v1/curriculos/{id}/adaptacoes` | Adaptar currículo para vaga |
| POST | `/v1/curriculos/{id}/analises-ats` | Analisar ATS |
| GET | `/v1/vagas` | Listar vagas salvas |
| POST | `/v1/vagas` | Salvar vaga |
| POST | `/v1/vagas/descobrir` | Descobrir vagas externas com match |
| GET | `/v1/candidaturas` | Listar candidaturas |
| POST | `/v1/candidaturas` | Criar candidatura |
| POST | `/v1/candidaturas/{id}/submissao` | Submeter candidatura |
| GET | `/v1/perfis` | Listar perfis |
| GET | `/v1/perfis/{id}` | Obter perfil |

A API começa pequena e cresce à medida que cada domínio é adaptado; a premissa é manter um router por domínio e um endpoint por caso de uso relevante.

## Pontos de Integração

- **SQLite**: repositórios `Impl` já existentes (`<dominio>/adapters/`) são reaproveitados. O path do banco vem de variável de ambiente.
- **Groq**: clients existentes (`AjustadorTextoClient`, `AnalisadorVagaClient` etc.) permanecem como adapters.
- **Fontes de vagas externas**: `BuscadorRemoteOk`, `BuscadorArbeitnow` etc. seguem no domínio `vaga_externa`.
- **Streamlit/frontend futuro**: consumirão a API via HTTP; nenhum import direto no backend.

## Abordagem de Testes

### Testes de unidade

- Manter testes existentes em `src/jobsync/tests/<dominio>/` passando.
- Criar `src/jobsync/tests/entrypoints/api/` para testar routers com `TestClient` do FastAPI usando fakes de repositórios.
- Criar testes de schemas Pydantic (validações de request/response).

### Testes de integração

- Subir o backend com `uvicorn` e fazer requisições reais contra `/docs`, `/openapi.json` e alguns endpoints com repositórios fake.
- Verificar se `import-linter` continua passando após adição de `entrypoints.api`.

## Sequenciamento de Desenvolvimento

### Ordem de construção

1. **Esqueleto FastAPI**: `main.py`, `dependencies.py`, exception handler e routers vazios.
2. **Repositórios prontos**: garantir que cada repositório `Impl` é injetável.
3. **Services expostos**: mapear DTOs de request/response para os `InputDto`/`OutputDto` existentes.
4. **Routers por domínio**: implementar endpoints da tabela acima, começando pelos domínios folha (`ats_score`, `token_captura`) e chegando aos complexos (`curriculo`, `vaga_externa`).
5. **OpenAPI/Swagger**: revisar títulos, descrições, exemplos e códigos de erro.
6. **Deploy**: `Dockerfile`, `.env.example`, instruções de startup.

### Dependências técnicas

- `fastapi` e `uvicorn` já estão em `requirements.txt`.
- Nenhuma nova dependência de infraestrutura externa é esperada.
- `import-linter` deve passar após adição de `jobsync.entrypoints.api`.

## Monitoramento e Observabilidade

- Logs via `logging` padrão; `uvicorn` expõe logs de acesso.
- Adicionar endpoint `/health` para health checks em deploy.
- Documentar variáveis de ambiente (`DATABASE_PATH`, `GROQ_API_KEY`, `CORS_ORIGINS`, `PORT`, `HOST`).

## Considerações Técnicas

### Decisões principais

- **Manter pacote `jobsync`**: o backend reaproveita o pacote `jobsync` em `src/`, evitando duplicar o domínio. O novo entrypoint fica em `src/jobsync/entrypoints/api/`.
- **Routers por domínio**: separação clara de responsabilidades e documentação OpenAPI agrupada por `tags`.
- **Schemas Pydantic distintos de entidades**: evita vazamento de detalhes internos e permite evoluir contrato sem mudar o domínio.
- **Versionamento no path**: `/v1/` visível e explícito para futuros clientes.
- **Deploy via container**: o backend pode subir sozinho com `uvicorn` e depois ser containerizado.

### Riscos conhecidos

- **Ciclos de importação**: adicionar `entrypoints.api` pode expor imports indiretos. Mitigação: `import-linter` e `TYPE_CHECKING`.
- **Acoplamento com Streamlit**: corre o risco de arrastar imports do Streamlit para o backend. Mitigação: revisar `dependencies.py` e proibir imports de `streamlit` em `entrypoints/api`.
- **Vazamento de entidades nos schemas**: se o `response_model` usar entidades de domínio, quebra o contrato. Mitigação: revisão de código e testes de router.
- **Dependências de infraestrutura em testes de API**: testes com repositórios reais podem ficar lentos. Mitigação: usar fakes para testes de API.

### Conformidade com padrões

- `code-design-standards.md` — estrutura por domínios, DTOs, `Service.executar`, separação de camadas.
- `back-end-general-rules.md` — REST, status codes, versionamento, Pydantic, `response_model`, exception handler.
- `general-rules.md` e `AGENTS.md` — Clean Code, DRY, KISS, DDD, Hexagonal, TDD.
- `testing-rules.md` — testes espelham a estrutura; testes de API com `TestClient`.

### Arquivos relevantes e dependentes

- `src/jobsync/entrypoints/api/main.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/entrypoints/api/exceptions.py`
- `src/jobsync/entrypoints/api/routers/*`
- `src/jobsync/entrypoints/api/schemas/*`
- `<dominio>/service_layer/*/service.py`
- `<dominio>/adapters/*_repository_impl.py`
- `requirements.txt`
- `setup.cfg`
- `Dockerfile`
- `.env.example`

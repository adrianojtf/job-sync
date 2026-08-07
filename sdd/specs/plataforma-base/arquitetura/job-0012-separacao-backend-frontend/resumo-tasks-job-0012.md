# Resumo de Tarefas — Separar job-sync em backend e frontend (JOB-0012)

## Visão Geral

Criar backend independente para o `job-sync`, isolando o hexágono de domínio e expondo as operações de negócio via FastAPI, com contrato OpenAPI e deploy independente.

## Tarefas

- [x] 01 Preparar projeto do backend: estrutura de pastas, `main.py`, `dependencies.py` e exception handler
- [x] 02 Adaptar/expor repositórios existentes como ports/adapters reutilizáveis pelo backend
- [x] 03 Mapear casos de uso para services e criar DTOs de request/response
- [x] 04 Implementar routers FastAPI v1, exception handler e documentação OpenAPI
- [x] 05 Preparar deploy independente (`Dockerfile`, `.env.example`, instruções de startup)

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 01 | Preparar projeto do backend | low | — | `pytest` passa na estrutura base; `import-linter` não acusa ciclos |
| 02 | Adaptar repositórios | medium | 01 | testes de repositórios reutilizados; fakes in-memory passam |
| 03 | Mapear casos de uso | high | 01 | testes unitários dos services; `executar` mantém comportamento |
| 04 | Implementar API FastAPI | high | 02, 03 | endpoints respondem com schemas corretos; `/docs` e `/openapi.json` acessíveis |
| 05 | Preparar deploy | medium | 04 | backend sobe via `uvicorn` na porta configurada; `Dockerfile` builda sem erros |

## Arquivos de origem

- PRD: `prd-job-0012.md`
- Tech Spec: `techspec-job-0012.md`

# Tarefa 01: Preparar projeto do backend

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar a estrutura base do backend, configurar o `FastAPI` e os pontos de entrada sem adicionar regras de negócio.

<requirements>
- Criar `src/jobsync/entrypoints/api/main.py`, `routers/__init__.py` e `dependencies.py`.
- Instanciar `FastAPI` com `title`, `version` e `description`, com prefixo `/v1` para routers.
- Configurar `CORS` e exception handler central via `back-end-general-rules.md`.
- Adicionar `uvicorn` como entrypoint em `README.md` ou `scripts/`.
- Garantir que `domain` e `service_layer` não importem nada de FastAPI.
</requirements>

## Subtarefas

- [ ] 1.1 Criar `src/jobsync/entrypoints/api/main.py` e pacote `routers/`.
- [ ] 1.2 Criar `src/jobsync/entrypoints/api/dependencies.py` com funções `Depends` para repositórios e services.
- [ ] 1.3 Criar `src/jobsync/entrypoints/api/exceptions.py` com handler padronizado.
- [ ] 1.4 Confirmar que `requirements.txt` já contém `fastapi`/`uvicorn`.
- [ ] 1.5 Rodar `pytest` e `lint-imports` para garantir que a estrutura não quebrou.

## Detalhes de Implementação

Ver `techspec-job-0012.md` -> Arquitetura do Sistema -> Visão Geral dos Componentes. O objetivo é ter um app FastAPI que consiga subir sem depender de cada domínio estar 100% exposto ainda.

## Critérios de Sucesso

- `python -m uvicorn src.jobsync.entrypoints.api.main:app --reload` sobe sem `ImportError`.
- `/docs` e `/openapi.json` retornam conteúdo (mesmo que esqueleto).
- `import-linter` não detecta ciclos e `domain` não importa `entrypoints`.

## Testes da Tarefa

- [ ] `pytest` continua passando.
- [ ] `lint-imports` passa.
- [ ] `uvicorn src.jobsync.entrypoints.api.main:app` levanta e responde em `/docs`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/main.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/entrypoints/api/exceptions.py`
- `src/jobsync/entrypoints/api/routers/__init__.py`
- `requirements.txt`
- `setup.cfg`

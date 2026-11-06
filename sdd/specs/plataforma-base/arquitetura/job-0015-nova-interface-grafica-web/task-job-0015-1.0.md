# Tarefa 1.0: Backend — CORS configurável e endpoint de token de captura

<critical>Ler os arquivos prd-job-0015.md e techspec-job-0015.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Fechar duas lacunas do backend que a nova UI precisa: gerar o token da extensão de navegador pela API `/v1` (hoje só existe no Streamlit) e restringir o CORS às origens configuradas.

- **Complexidade:** low
- **Dependências:** nenhuma

<requirements>
- Criar `POST /v1/tokens-captura` que usa o service existente `CriarTokenCaptura`, retornando `201`.
- Request `{ perfil_identificador }` e response `{ token, perfil_identificador }` em schemas Pydantic próprios.
- Erros no formato `ProblemaResponse`. Não registrar o valor do token em log.
- CORS lê `CORS_ORIGINS` (lista separada por vírgula, padrão `*` em dev) e usa `allow_credentials=False`.
- Nenhuma mudança em `domain/` ou `service_layer/`.
- Documentação OpenAPI completa: `summary`, `description`, `response_model` e exemplos.
</requirements>

## Subtarefas

- [x] 1.1 Escrever os testes do router (red): 201 com token e 422 sem `perfil_identificador`.
- [x] 1.2 Criar `schemas/token_captura.py` com `TokenCapturaCriarRequest` e `TokenCapturaResponse`.
- [x] 1.3 Adicionar `ServiceCriarTokenCapturaDep` em `api/dependencies.py`.
- [x] 1.4 Criar `routers/token_captura_router.py` e registrar em `main.py` com prefixo `/v1`.
- [x] 1.5 Ler `CORS_ORIGINS` em `main.py` e ajustar `allow_credentials`.
- [x] 1.6 Adicionar a requisição na `job-sync.postman_collection.json`.

## Detalhes de Implementação

Ver `techspec-job-0015.md` → "Endpoints de API → Novos (backend)", e a linha de CORS em "Riscos Conhecidos". Seguir o padrão de `vaga_router.py` (schemas com `to_dto`/`from_dto`, DI com `Annotated`).

## Critérios de Sucesso

- `POST /v1/tokens-captura` aparece em `/docs` com exemplo.
- Um token gerado pela API é aceito pelo `servidor_captura.py` (`POST /api/vagas/capturar`).
- Com `CORS_ORIGINS=http://localhost:5173`, outra origem não recebe `Access-Control-Allow-Origin`.

## Testes da Tarefa

- [x] Testes de unidade: `TestTokenCapturaRouter` (201, 422), com fake in-memory do repositório.
- [x] Teste de CORS: origem permitida recebe o header e origem não listada não recebe.
- [x] `pytest` e `lint-imports` passam.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/main.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/entrypoints/api/routers/token_captura_router.py` (novo)
- `src/jobsync/entrypoints/api/schemas/token_captura.py` (novo)
- `src/jobsync/token_captura/service_layer/criar_token_captura/service.py`
- `src/jobsync/tests/entrypoints/api/`
- `.env.example`
- `job-sync.postman_collection.json`

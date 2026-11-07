# Tarefa 4.0: Endpoints de rascunho e de PDF revisado

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expor o rascunho e a confirmação na API.

<requirements>
- Schemas `RascunhoCurriculoAdaptadoSchema` (to_domain/from_domain), `RascunhoAdaptadoResponse`, `GerarPdfCurriculoRevisadoRequest`, `CurriculoRevisadoResponse`.
- `POST /curriculos/{id}/rascunhos-adaptados` → 200.
- `POST /curriculos-revisados` → 200 JSON; `?download=true` → `application/pdf`; 422 para rascunho inválido.
- Atualizar `job-sync.postman_collection.json`.
- Complexidade: medium. Dependências: 3.0.
</requirements>

## Subtarefas

- [ ] 4.1 Testes de schema e router (Red).
- [ ] 4.2 Schemas.
- [ ] 4.3 Endpoints.
- [ ] 4.4 Postman.

## Detalhes de Implementação

Ver "Modelos de Dados" e "Endpoints de API" em `techspec-job-0033.md`.

## Critérios de Sucesso

- Endpoints documentados no OpenAPI e cobertos por testes (sucesso, 422, download).

## Testes da Tarefa

- [ ] Testes de schema e router.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/schemas/curriculo.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/tests/entrypoints/api/`
- `job-sync.postman_collection.json`

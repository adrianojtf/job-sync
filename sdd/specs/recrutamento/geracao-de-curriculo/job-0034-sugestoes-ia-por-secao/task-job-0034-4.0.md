# Tarefa 4.0: Endpoints de sugestão e análise da vaga no rascunho

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expor as sugestões na API e fazer o rascunho da JOB-0033 devolver a análise da vaga.

<requirements>
- `POST /secoes-curriculo/sugestoes` e `POST /experiencias-profissionais/sugestoes` (200, 422, 502).
- Schemas de requisição e resposta; `contexto_vaga` opcional.
- `RascunhoAdaptadoResponse` ganha `analise_vaga`.
- DI dos dois casos de uso; atualizar `job-sync.postman_collection.json`.
- Complexidade: medium. Dependências: 3.0.
</requirements>

## Subtarefas

- [ ] 4.1 Testes de schema e router (Red).
- [ ] 4.2 Schemas.
- [ ] 4.3 Endpoints e DI.
- [ ] 4.4 Postman.

## Detalhes de Implementação

Ver "Endpoints de API" e "Modelos de Dados" em `techspec-job-0034.md`.

## Critérios de Sucesso

- Endpoints cobertos por testes de sucesso, 422 e 502; contratos anteriores inalterados.

## Testes da Tarefa

- [ ] Testes de schema e router.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/`
- `src/jobsync/tests/entrypoints/api/`
- `job-sync.postman_collection.json`

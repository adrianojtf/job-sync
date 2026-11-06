# Tarefa 5.0: API

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expor o novo formato e a nova sugestão na API.

<requirements>
- `ExperienciaRascunhoSchema` com `conquistas` e `contexto`.
- `POST /v1/experiencias-adaptadas/sugestoes` (200, 422, 502) com `contexto_vaga` obrigatório.
- `/experiencias-profissionais/sugestoes` perde `contexto_vaga`.
- `para_curriculo` recebe o idioma nos fluxos de PDF; injeção e Postman.
- Complexidade: medium. Dependências: 3.0, 4.0.
</requirements>

## Subtarefas

- [ ] 5.1 Testes de schema e router (Red).
- [ ] 5.2 Schemas.
- [ ] 5.3 Endpoints e injeção.
- [ ] 5.4 Postman.

## Detalhes de Implementação

Ver "Endpoints de API" em `techspec-job-0035.md`.

## Critérios de Sucesso

- Endpoints cobertos por testes de sucesso, 422 e 502.

## Testes da Tarefa

- [ ] Testes de schema e router.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/`
- `src/jobsync/tests/entrypoints/api/`
- `job-sync.postman_collection.json`

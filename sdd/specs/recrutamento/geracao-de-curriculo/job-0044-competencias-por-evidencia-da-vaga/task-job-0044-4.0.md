# Tarefa 4.0: API e tipos: `lacunas_tecnologia` no schema, `schema.d.ts` e Postman

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expõe as lacunas na resposta do rascunho e atualiza os tipos do frontend.

Complexidade: low.

<requirements>
- `RascunhoCurriculoAdaptadoSchema.lacunas_tecnologia` na resposta; ignorado na entrada.
- `schema.d.ts` regenerado; a collection Postman confere a propriedade.
</requirements>

## Subtarefas

- [ ] 4.1 Testes de schema e router (red).
- [ ] 4.2 Implementar o schema (green).
- [ ] 4.3 Regenerar `schema.d.ts` e atualizar o Postman.

## Detalhes de Implementação

Techspec: "Design de Implementação" e "Abordagem de Testes". PRD: requisitos funcionais correspondentes.

## Critérios de Sucesso

- Os requisitos acima passam nos testes da tarefa.
- Nenhuma regressão nas JOB-0037, JOB-0040 e JOB-0041.

## Testes da Tarefa

- [ ] Testes de unidade de schema e router.
- [ ] Regressão: `src/jobsync/tests/entrypoints/api/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/schemas/curriculo.py`
- `frontend/src/api/schema.d.ts`
- `job-sync.postman_collection.json`

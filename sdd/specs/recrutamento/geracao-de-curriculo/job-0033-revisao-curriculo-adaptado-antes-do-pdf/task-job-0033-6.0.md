# Tarefa 6.0: Cliente de API e tipos do frontend

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Atualizar o contrato tipado e o cliente HTTP com os novos endpoints.

<requirements>
- Regenerar `api/schema.d.ts` a partir do OpenAPI.
- Aliases em `tipos.ts`.
- Métodos `gerarRascunhoAdaptado` e `gerarPdfCurriculoRevisado` em `ApiClient` e `HttpApiClient` (com `ia: true` no rascunho).
- Complexidade: low. Dependências: 4.0.
</requirements>

## Subtarefas

- [ ] 6.1 Regenerar tipos.
- [ ] 6.2 Cliente HTTP e testes.

## Detalhes de Implementação

Ver "Endpoints de API" em `techspec-job-0033.md`.

## Critérios de Sucesso

- Tipos compilam; testes do cliente cobrem os novos métodos.

## Testes da Tarefa

- [ ] Testes de unidade de `http-api-client`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/api/`

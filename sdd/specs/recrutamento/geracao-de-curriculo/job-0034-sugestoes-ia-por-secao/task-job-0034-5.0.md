# Tarefa 5.0: Cliente de API e tipos do frontend

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Atualizar o contrato tipado e o cliente com as sugestões.

<requirements>
- Regenerar `schema.d.ts`; aliases em `tipos.ts`.
- `sugerirAjusteSecao` e `sugerirAjusteExperiencia` em `ApiClient` e `HttpApiClient` com `ia: true`.
- Complexidade: low. Dependências: 4.0.
</requirements>

## Subtarefas

- [ ] 5.1 Regenerar tipos.
- [ ] 5.2 Métodos e testes.

## Detalhes de Implementação

Ver "Visão Geral dos Componentes" (frontend) em `techspec-job-0034.md`.

## Critérios de Sucesso

- Tipos compilam; testes do cliente cobrem os dois métodos.

## Testes da Tarefa

- [ ] Testes de unidade de `http-api-client`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/api/`

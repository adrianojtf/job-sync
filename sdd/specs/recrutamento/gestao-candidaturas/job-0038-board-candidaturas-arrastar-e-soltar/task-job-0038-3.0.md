# Tarefa 3.0: Contrato e cliente de API no frontend

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

O frontend passa a enviar a posição ao mover uma candidatura e a receber `posicao` na resposta. Os tipos vêm do contrato OpenAPI regenerado.

<requirements>
- Regenerar `schema.d.ts` com `npm run gerar-tipos`, usando Python 3.12 (o mesmo do CI).
- `moverCandidatura(id, novoStatus, posicao?)` na interface `ApiClient` e no `HttpApiClient`; o corpo inclui `posicao` só quando informada.
- Ajustar fakes e mocks de `ApiClient` usados nos testes.
</requirements>

## Subtarefas

- [x] 3.1 Escrever o teste do `HttpApiClient` com e sem `posicao` (red).
- [x] 3.2 Regenerar o schema e conferir `tipos.ts`.
- [x] 3.3 Implementar a assinatura nova na interface e no cliente HTTP.
- [x] 3.4 Ajustar mocks e fakes existentes.

## Detalhes de Implementação

Techspec: "Visão Geral dos Componentes" (frontend, `api/*`) e "Pontos de Integração".

## Critérios de Sucesso

- `schema.d.ts` sem diferença no CI depois de regenerado.
- `tsc -b` e `eslint` sem erros.

## Testes da Tarefa

- [x] `http-api-client.test.ts`: corpo com `posicao` quando informada, sem o campo quando omitida, e conversão de 404 e 422 em `ApiError`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/api/api-client.ts`
- `frontend/src/api/http-api-client.ts`
- `frontend/src/api/schema.d.ts`
- `frontend/src/api/tipos.ts`
- `frontend/src/api/http-api-client.test.ts`
- `frontend/src/test/`

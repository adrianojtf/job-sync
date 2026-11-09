# Tarefa 5.0: Cliente de API e tipos do frontend

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Levar o contrato novo para o frontend: regenerar os tipos do OpenAPI e criar o método do cliente de API.

<requirements>
- Regenerar `frontend/src/api/schema.d.ts` com `npm run gerar-tipos`, subindo o backend **com Python 3.12**, o mesmo do CI (com 3.13 a descrição padrão do 422 muda e o passo de contrato falha).
- Adicionar `ConfirmarCandidaturaEntrada` (a partir de `Esquemas["CandidaturaConfirmarRequest"]`) em `api/tipos.ts`.
- Adicionar `confirmarCandidaturaAjustada(dados): Promise<Candidatura>` em `api/api-client.ts` e `http-api-client.ts`.
- Erros 409 e 422 viram `ApiError` pelo caminho já usado pelos outros métodos.
- Se os testes das tarefas 5.0 e 6.0 precisarem simular o endpoint, adicionar o handler em `frontend/src/test/servidor-api.ts` e a fixture em `frontend/src/test/fixtures.ts`.
</requirements>

## Subtarefas

- [ ] 5.1 Escrever os testes do `HttpApiClient` (red).
- [ ] 5.2 Regenerar o `schema.d.ts` com Python 3.12.
- [ ] 5.3 Criar o tipo de entrada e o método no cliente.
- [ ] 5.4 Adicionar o handler e a fixture do endpoint ao servidor de API de teste.

## Detalhes de Implementação

Consultar em `techspec-job-0037.md` a seção "Frontend" e, em `README.md`, o passo de geração do contrato.

## Critérios de Sucesso

- `npm run` do typecheck e dos testes sem erro de tipo.
- O passo de contrato do CI não acusa diferença no `schema.d.ts`.

## Testes da Tarefa

- [ ] O método envia `POST /v1/candidaturas-ajustadas` com o corpo esperado.
- [ ] Resposta 201 devolve a candidatura.
- [ ] Resposta 409 vira `ApiError` com a mensagem do problema.
- [ ] Resposta 422 vira `ApiError`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/api/schema.d.ts`
- `frontend/src/api/tipos.ts`
- `frontend/src/api/api-client.ts`
- `frontend/src/api/http-api-client.ts`
- `frontend/src/api/http-api-client.test.ts`
- `frontend/src/test/servidor-api.ts`
- `frontend/src/test/fixtures.ts`
- `README.md` (comando `gerar-tipos`)

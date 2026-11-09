# Tarefa 5.0: Cliente de API e tipos do frontend

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Levar o contrato novo para o frontend: regenerar os tipos do OpenAPI e criar o método do cliente de API.

<requirements>
- Regenerar `frontend/src/api/schema.d.ts` com `npm run gerar-tipos`, subindo o backend **com Python 3.12**, o mesmo do CI (com 3.13 a descrição padrão do 422 muda e o passo de contrato falha).
- Adicionar `ConfirmarCandidaturaEntrada` (a partir de `Esquemas["CandidaturaConfirmarRequest"]`) em `api/tipos.ts`.
- Adicionar `confirmarCandidaturaAjustada(dados): Promise<Candidatura>` em `api/api-client.ts` e `http-api-client.ts`.
- Erros 409 e 422 viram `ApiError` pelo caminho já usado pelos outros métodos.
- Os testes que simulam o endpoint registram o handler com `servidorApi.use(...)`, como os demais testes de escrita; o servidor de teste compartilhado não muda.
</requirements>

## Subtarefas

- [x] 5.1 Escrever os testes do `HttpApiClient` (red).
- [x] 5.2 Regenerar o `schema.d.ts` com Python 3.12.
- [x] 5.3 Criar o tipo de entrada e o método no cliente.
- [x] 5.4 Verificar o servidor de API de teste. Nenhuma mudança foi necessária: ele só traz respostas padrão para leituras, as escritas são registradas em cada teste (`servidorApi.use`) e a fixture `CANDIDATURA` já existe. O handler do endpoint novo fica no teste da tela, na tarefa 6.0.

## Detalhes de Implementação

Consultar em `techspec-job-0037.md` a seção "Frontend" e, em `README.md`, o passo de geração do contrato.

## Critérios de Sucesso

- `npm run` do typecheck e dos testes sem erro de tipo.
- O passo de contrato do CI não acusa diferença no `schema.d.ts`.

## Testes da Tarefa

- [x] O método envia `POST /v1/candidaturas-ajustadas` com o corpo esperado.
- [x] Resposta 201 devolve a candidatura.
- [x] Resposta 409 vira `ApiError` com a mensagem do problema.
- [x] Resposta 422 vira `ApiError`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/api/schema.d.ts`
- `frontend/src/api/tipos.ts`
- `frontend/src/api/api-client.ts`
- `frontend/src/api/http-api-client.ts`
- `frontend/src/api/http-api-client.test.ts`
- `frontend/src/test/servidor-api.ts` e `fixtures.ts` (referência, sem mudança)
- `README.md` (comando `gerar-tipos`)

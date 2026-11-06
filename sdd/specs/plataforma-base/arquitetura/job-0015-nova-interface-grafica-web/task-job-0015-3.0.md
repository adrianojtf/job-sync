# Tarefa 3.0: Fundação do frontend — projeto, testes, tipos do OpenAPI e ApiClient

<critical>Ler os arquivos prd-job-0015.md e techspec-job-0015.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar o projeto `frontend/` (React 18 + TypeScript + Vite) com a infraestrutura que todas as telas usam: testes, tipos gerados do contrato da API e o port `ApiClient` com o adapter HTTP.

- **Complexidade:** high
- **Dependências:** 1.0, 2.0 (para os tipos já incluírem os endpoints novos)

<requirements>
- Projeto Vite + React + TS em `frontend/`, com `package.json`, `tsconfig.json` (modo `strict`) e `vite.config.ts` próprios.
- Proxy de desenvolvimento `/v1 → http://localhost:8000`. Base URL via `VITE_API_BASE_URL`.
- Lint (ESLint) e formatação (Prettier).
- Vitest + Testing Library + MSW configurados.
- Script `npm run gerar-tipos` que gera `src/api/schema.d.ts` com `openapi-typescript` a partir de `/openapi.json`.
- `api/api-client.ts` (port) com um método por operação listada na Tech Spec e `api/http-api-client.ts` (adapter com `fetch`).
- Timeout de 180 s nas rotas de IA e de 15 s nas demais. `ProblemaResponse` convertido em `ApiError`.
- `ApiClientProvider` (contexto React) e `QueryClientProvider` (TanStack Query).
- Utilitários `shared/arquivos`: `File → base64`, `base64 → Blob` e download.
</requirements>

## Subtarefas

- [ ] 3.1 Scaffold Vite + React + TS, ESLint, Prettier e scripts `dev`, `build`, `test`, `lint`.
- [ ] 3.2 Configurar Vitest, Testing Library e MSW (handlers base em `src/test/`).
- [ ] 3.3 Script `gerar-tipos` e primeira geração de `schema.d.ts`. Reexportar nomes de domínio em `api/tipos.ts`.
- [ ] 3.4 Escrever os testes do `HttpApiClient` (red) e implementar o adapter.
- [ ] 3.5 Implementar `ApiClient`, `ApiClientProvider` e `QueryClientProvider`.
- [ ] 3.6 Implementar e testar os utilitários de arquivo.

## Detalhes de Implementação

Ver `techspec-job-0015.md` → "Visão Geral dos Componentes", "Interfaces Principais", "Pontos de Integração" e "Decisões Principais". As telas não chamam `fetch` direto: sempre via `ApiClient`.

## Critérios de Sucesso

- `npm run dev` sobe e chama `GET /v1/health` pelo proxy.
- `npm run build`, `npm run lint` e `npm test` passam.
- `schema.d.ts` contém `/v1/tokens-captura` e `/v1/vagas/descobertas/candidaturas`.
- Mudar um campo no backend e regenerar os tipos quebra a compilação onde ele é usado.

## Testes da Tarefa

- [ ] Testes de unidade do `HttpApiClient`: URL base, timeout, 204 sem corpo, 404, 422 e 500 viram `ApiError` com `status`, `title` e `detail`.
- [ ] Testes de unidade de `base64ParaBlob` e `arquivoParaBase64`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json` (novos)
- `frontend/src/api/schema.d.ts`, `api-client.ts`, `http-api-client.ts`, `tipos.ts` (novos)
- `frontend/src/shared/arquivos/` (novo)
- `frontend/src/test/` (novo)
- `src/jobsync/entrypoints/api/main.py` (fonte do `openapi.json`)
- `.gitignore` (`node_modules`, `dist`)

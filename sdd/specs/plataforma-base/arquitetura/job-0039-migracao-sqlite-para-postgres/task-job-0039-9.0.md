# Tarefa 9.0: E2E e CI completo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Faz os testes E2E e o CI rodarem sobre Postgres.

<requirements>
- `frontend/playwright.config.ts` e `tests/e2e/app_e2e.py` usam `DATABASE_URL` (banco `job_sync_e2e`) e recriam as tabelas vazias antes da execução.
- Serviço `postgres:16` com healthcheck no job `e2e` do CI.
- O job de contrato da API continua sem diferença em `schema.d.ts`.
- Remover o diretório de dados `.db` do E2E e ajustar `.gitignore` se necessário.
</requirements>

## Subtarefas

- [ ] 9.1 Ajustar `app_e2e.py` para Postgres e limpeza do banco.
- [ ] 9.2 Ajustar `playwright.config.ts`.
- [ ] 9.3 Adicionar o serviço Postgres ao job `e2e` e a variável `DATABASE_URL`.
- [ ] 9.4 Rodar E2E, axe e contrato OpenAPI localmente.

## Detalhes de Implementação

Techspec: "Testes E2E" e "Endpoints de API". PRD: RF-02.

## Critérios de Sucesso

- E2E do board e demais fluxos passam sobre Postgres.
- Sem diff em `frontend/src/api/schema.d.ts`.

## Testes da Tarefa

- [ ] Suíte Playwright completa.
- [ ] Geração de tipos do OpenAPI sem diferença.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/playwright.config.ts`
- `src/jobsync/tests/e2e/app_e2e.py`
- .github/workflows/ci.yml
- .gitignore

# Tarefa 9.0: E2E, acessibilidade e suíte completa

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Validar o fluxo completo com os dublês determinísticos e rodar todas as suítes.

<requirements>
- E2E: a revisão mostra a lista de ajustes; dois pedidos seguidos de sugestão mostram focos diferentes; aplicar e gerar o PDF.
- Acessibilidade (axe) com a lista e o foco.
- Suíte completa: pytest, Vitest, lint, `tsc`, build, contrato com Python 3.12.
- Atualizar o resumo de tarefas com desvios, validação realizada e pontos em aberto.
- Complexidade: medium. Dependências: 7.0, 8.0.
</requirements>

## Subtarefas

- [ ] 9.1 Cenários em `fluxos.spec.ts`.
- [ ] 9.2 Cenários em `acessibilidade.spec.ts`.
- [ ] 9.3 Suíte completa.
- [ ] 9.4 Resumo de tarefas atualizado.

## Detalhes de Implementação

Ver "Testes de Serviço" em `techspec-job-0037.md`.

## Critérios de Sucesso

- Todas as suítes verdes.
- Resumo registra o que não foi validado com a IA real.

## Testes da Tarefa

- [ ] E2E e acessibilidade (Playwright); suítes de backend e frontend.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/e2e/{fluxos.spec.ts,acessibilidade.spec.ts,apoio.ts}`
- `src/jobsync/tests/e2e/app_e2e.py`
- `resumo-tasks-job-0037.md`

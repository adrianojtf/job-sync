# Tarefa 8.0: E2E, acessibilidade e fechamento

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cobre com testes de ponta a ponta o que o jsdom não consegue testar (arrasto por ponteiro, layout e toque), roda axe e fecha a suíte completa.

<requirements>
- E2E: arrastar com o mouse entre colunas e dentro da coluna, recarregar e conferir a persistência.
- E2E: clique no título abre o detalhe; arrasto não abre; "Mover para" no detalhe move a candidatura e o board reflete.
- E2E: larguras 375, 768 e 1280 px sem rolagem horizontal da página, com a área do board rolando.
- E2E: viewport móvel com emulação de toque (rolagem da página e arrasto após toque longo).
- axe na tela de Candidaturas com cartões e durante o arrasto por teclado.
- Suítes completas verdes: `pytest`, Vitest, `npm run lint`, `npm run build`, `npm run e2e` e `lint-imports`.
- Marcar as tarefas como concluídas no `resumo-tasks-job-0038.md`.
</requirements>

## Subtarefas

- [x] 8.1 Ajustar `frontend/e2e/apoio.ts` para criar candidaturas em mais de uma coluna.
- [x] 8.2 Escrever os E2E de arrasto, persistência, título e "Mover para".
- [x] 8.3 Escrever os E2E de largura e de toque.
- [x] 8.4 Estender `acessibilidade.spec.ts`.
- [x] 8.5 Rodar todas as suítes e corrigir o que falhar.

## Detalhes de Implementação

Techspec: "Abordagem de Testes" (Testes de Serviço). PRD: critérios de sucesso em "Objetivos".

## Critérios de Sucesso

- 100% das movimentações persistem após recarregar.
- Nenhuma violação grave no axe.
- Todas as suítes e linters verdes.

## Testes da Tarefa

- [x] Todos os E2E e axe listados acima.
- [x] Suíte completa de backend e frontend.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/e2e/fluxos.spec.ts`
- `frontend/e2e/acessibilidade.spec.ts`
- `frontend/e2e/apoio.ts`
- frontend/playwright.config.ts (conferir os projetos de viewport)
- `sdd/specs/recrutamento/gestao-candidaturas/job-0038-board-candidaturas-arrastar-e-soltar/resumo-tasks-job-0038.md`

# Tarefa 2.0: Frontend: periodo.ts, limites.ts e validação por campo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Espelha no frontend a validação e a ordenação do período, a constante do limite e a validação por campo da lista.

<requirements>
- `periodo.ts`: `validarPeriodo`, `validarAno`, `inicioDoPeriodo` e `ordenarPorPeriodo` (mais recente primeiro; `Atual` vale como o mais recente; vazio no fim mantendo a ordem relativa; desempate estável).
- `limites.ts`: `LIMITE_DE_ITENS = 15`.
- `CampoItem.validar` opcional em `campos-curriculo.ts`, usado por `ListaItensCurriculo` como `validate` do campo.
- O Vitest lê a mesma tabela `periodo.casos.json` da task 1.0.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 2.1 Escrever os testes de `periodo.ts` com a tabela compartilhada (red).
- [ ] 2.2 Implementar `periodo.ts`, `limites.ts` e `CampoItem.validar` (green).
- [ ] 2.3 Refatorar e rodar `npm test`.

## Detalhes de Implementação

Techspec: "Visão Geral dos Componentes" (frontend) e "Modelos de Dados". PRD: RF 20 a 22.

Complexidade: low. Dependências: 1.0.

## Critérios de Sucesso

- Os mesmos casos válidos e inválidos do backend têm o mesmo resultado no frontend.
- A mensagem de erro traz um exemplo de formato.

## Testes da Tarefa

- [ ] Vitest de `periodo.ts`.
- [ ] Regressão: `npm test` em `frontend/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/periodo.ts (novo)`
- `frontend/src/shared/formulario-curriculo/periodo.test.ts (novo)`
- `frontend/src/shared/formulario-curriculo/limites.ts (novo)`
- `frontend/src/shared/formulario-curriculo/campos-curriculo.ts`
- `frontend/src/shared/formulario-curriculo/ListaItensCurriculo.tsx`

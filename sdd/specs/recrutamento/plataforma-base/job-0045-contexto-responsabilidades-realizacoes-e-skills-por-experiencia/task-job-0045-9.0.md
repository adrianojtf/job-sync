# Tarefa 9.0: Frontend: revisão do adaptado e EditorTags com arrastar e soltar entre categorias

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

A tela de revisão do currículo adaptado edita os quatro blocos, e as tags de competências podem ser reordenadas e movidas entre categorias por arrastar e soltar, também pelo teclado.

<requirements>
- `RevisaoCurriculoAdaptado`, `formulario-revisao.ts`, `campos-curriculo.ts` e `SugestaoExperienciaAdaptada` com os quatro blocos e as sugestões de IA por experiência devolvendo os quatro blocos.
- Skills da experiência em tags, pelo `EditorTags` da task 8.0.
- `EditorCompetencias` com `@dnd-kit/core` e `@dnd-kit/sortable` (já instalados): reordenar dentro da categoria e mover entre categorias (PRD RF 31 a 34).
- Regras de movimento em `competencias.ts` (sem duplicar tag na categoria destino, ignorando caixa; categoria vazia descartada ao salvar), testáveis sem DOM.
- Acessibilidade: `sortableKeyboardCoordinates` e anúncio do movimento em `role="status"`.
- Aviso de números estimados no topo da revisão.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 9.1 Escrever os testes de `competencias.ts`, do editor e da revisão (red).
- [x] 9.2 Implementar as regras de movimento em `competencias.ts` (green).
- [x] 9.3 Implementar o arrastar e soltar no `EditorCompetencias` (green).
- [x] 9.4 Adaptar a revisão, o formulário e a sugestão por experiência (green).
- [x] 9.5 Refatorar e rodar o Vitest.

## Detalhes de Implementação

Techspec: "Modelos de Dados" (Drag and drop). O teste do dnd-kit segue o mock de `features/candidaturas/CandidaturasPage.test.tsx`. PRD: RF 22 a 25 e 31 a 34.

Complexidade: high. Dependências: 6.0, 7.0.

## Critérios de Sucesso

- Mover uma tag entre categorias pelo mouse e pelo teclado funciona, sem duplicar nem perder tags.
- A revisão salva e abre o currículo com os quatro blocos.

## Testes da Tarefa

- [x] Vitest: `competencias.test.ts`, `EditorCompetencias.test.tsx`, `formulario-revisao.test.ts` e `RevisaoCurriculoAdaptado.test.tsx`.
- [x] Regressão: `npm test` em `frontend/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/competencias.ts`
- `frontend/src/shared/formulario-curriculo/EditorCompetencias.tsx`
- `frontend/src/shared/formulario-curriculo/campos-curriculo.ts`
- `frontend/src/features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx`
- `frontend/src/features/ajustar-vaga/formulario-revisao.ts`
- `frontend/src/features/ajustar-vaga/SugestaoExperienciaAdaptada.tsx`
- `frontend/src/features/candidaturas/CandidaturasPage.test.tsx (referência de mock)`

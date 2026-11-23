# Tarefa 4.0: Componente `EditorCompetencias` integrado à revisão

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cria o editor de competências por categorias e tags e o usa na revisão do currículo adaptado no lugar do campo de texto de tecnologias.

<requirements>
- Cada categoria tem nome editável, tags com botão de remover e campo para nova tag.
- Tag nova é criada com Enter ou vírgula; tag duplicada na categoria (sem diferenciar caixa) e vazia são ignoradas.
- É possível criar, renomear e excluir categorias.
- Tudo funciona por teclado; botão de remover tem nome acessível com o texto da tag (ex.: "Remover Java"); criar e remover tag é anunciado por região `aria-live`.
- O bloco usa `react-hook-form` (`useFieldArray`) como o restante da revisão.
- A confirmação da revisão envia `competencias` no rascunho; "Sugestões de IA" de tecnologias continua funcionando sobre o texto das categorias.
- O restante da revisão não muda.
</requirements>

## Subtarefas

- [ ] 4.1 Testes do `EditorCompetencias` (red): remover, criar com Enter e vírgula, duplicada, renomear, criar e excluir categoria, rótulos acessíveis.
- [ ] 4.2 Testes de `formulario-revisao.ts`: ida e volta entre rascunho e formulário com competências (red).
- [ ] 4.3 Implementar `EditorCompetencias.tsx` e o css (green).
- [ ] 4.4 Integrar em `RevisaoCurriculoAdaptado.tsx` e `formulario-revisao.ts`, retirando o textarea de tecnologias quando houver `competencias` (green).
- [ ] 4.5 Adaptar a "Sugestão de IA" de tecnologias para ler e aplicar o texto das categorias.
- [ ] 4.6 Atualizar os testes de `RevisaoCurriculoAdaptado.test.tsx`.

## Detalhes de Implementação

Techspec: "Componentes" (frontend) e "Abordagem de Testes". PRD: RF 1 a 4 e 7, Experiência do Usuário e Acessibilidade. Reaproveitar os componentes de `shared/ui` e os padrões de `shared/formulario-curriculo`.

## Critérios de Sucesso

- Remover ou incluir uma tecnologia leva uma ação, sem editar texto corrido.
- A confirmação gera o PDF com as categorias e tags editadas.
- Lint, tipos e testes do frontend passam.

## Testes da Tarefa

- [ ] Testes de unidade (Vitest e Testing Library).
- [ ] Regressão: `frontend/src/features/ajustar-vaga/` e `frontend/src/shared/formulario-curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/EditorCompetencias.tsx` (novo)
- `frontend/src/features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx`
- `frontend/src/features/ajustar-vaga/formulario-revisao.ts`
- `frontend/src/shared/formulario-curriculo/use-sugestoes.ts`
- `frontend/src/api/tipos`

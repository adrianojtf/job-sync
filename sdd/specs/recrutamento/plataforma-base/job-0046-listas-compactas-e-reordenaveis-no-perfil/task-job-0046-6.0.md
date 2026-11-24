# Tarefa 6.0: Tecnologias como tags reordenáveis

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

As tecnologias gerais deixam de ser um texto separado por vírgula e passam a ser tags que se criam, excluem e reordenam.

<requirements>
- `tecnologias: string[]` em `FormularioPerfil`, com conversões em `formulario-perfil.ts` (a API já usa lista).
- `ListaDeTecnologias.tsx`: `EditorTags` com `arrastavel` dentro de um `DndContext`, reaproveitando `soltarTag` com a lista tratada como uma categoria, anúncios em português e desfazer.
- Tecnologia repetida (sem diferenciar caixa) não é criada.
- A sincronia de skills continua acrescentando no fim ao salvar, e o aviso de tecnologias incluídas segue igual.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 6.1 Escrever os testes do componente e das conversões (red).
- [x] 6.2 Implementar `ListaDeTecnologias` e ajustar `formulario-perfil.ts` (green).
- [x] 6.3 Refatorar e rodar `npm test`.

## Detalhes de Implementação

Techspec: "Decisões Principais" e "Modelos de Dados". PRD: RF 10 a 12.

Complexidade: medium. Dependências: 3.0.

## Critérios de Sucesso

- Criar, excluir e reordenar tags funciona por mouse e teclado.
- O corpo enviado à API é o mesmo formato atual.

## Testes da Tarefa

- [x] Vitest de `ListaDeTecnologias` e de `formulario-perfil`.
- [x] Regressão: `npm test`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/ListaDeTecnologias.tsx (novo)`
- `frontend/src/shared/formulario-curriculo/ListaDeTecnologias.test.tsx (novo)`
- `frontend/src/shared/formulario-curriculo/EditorTags.tsx`
- `frontend/src/shared/formulario-curriculo/competencias.ts`
- `frontend/src/features/perfil/formulario-perfil.ts`
- `frontend/src/features/perfil/formulario-perfil.test.ts`

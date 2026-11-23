# Tarefa 4.0: Frontend: banco de conquistas em Meu perfil com aviso de duplicidade

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Permite ao usuário cadastrar, editar e excluir conquistas em cada experiência do perfil e vê o aviso quando a nova conquista se parece com outra.

<requirements>
- `formulario-perfil.ts` mapeia `conquistas` por experiência, do `GET` ao formulário e do formulário ao `PUT`.
- `PerfilPage.tsx`: lista de conquistas por experiência, com cadastro, edição e exclusão diretos.
- Ao cadastrar, chamar `POST /perfil-estruturado/conquistas/parecidas` e mostrar a conquista parecida, com as ações "Salvar mesmo assim" e "Cancelar".
- O aviso de revisão existente continua visível; campos e avisos acessíveis por teclado e leitor de tela.
- Experiência sem conquistas continua funcionando como hoje.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 4.1 Escrever os testes de `formulario-perfil` (red) e mapear `conquistas`.
- [x] 4.2 Escrever os testes de `PerfilPage` (red): lista, cadastro, edição, exclusão.
- [x] 4.3 Implementar o componente da lista de conquistas e o uso na página (green).
- [x] 4.4 Escrever os testes do aviso de duplicidade (red) e implementar o hook e o aviso (green).
- [x] 4.5 Revisar acessibilidade e rodar o lint e os testes do frontend.

## Detalhes de Implementação

Techspec: "Visão Geral dos Componentes" (frontend) e "Endpoints de API". PRD: RF 2, 5, 15 e 16 e a seção Experiência do Usuário. Não há migração de dados do usuário.

## Critérios de Sucesso

- O usuário cadastra, edita e exclui conquistas por experiência e salva o perfil.
- Conquista parecida mostra o aviso e deixa o usuário decidir.
- `npm run lint` e os testes do frontend passam.

## Testes da Tarefa

- [x] Testes vitest de `formulario-perfil` e `PerfilPage`.
- [x] `npm run lint` no `frontend/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/perfil/PerfilPage.tsx`
- `frontend/src/features/perfil/formulario-perfil.ts`
- `frontend/src/features/perfil/use-perfil-estruturado.ts`
- `frontend/src/features/perfil/PerfilPage.test.tsx`
- `frontend/src/features/perfil/formulario-perfil.test.ts`

## Resultado da execução

- `ConquistasDaExperiencia` em `features/perfil`, método `verificarConquistasParecidas` no cliente da API e tipos regenerados (`npm run gerar-tipos`, só adições).
- Sugestões e avaliação de IA continuam recebendo a experiência sem as conquistas (`experienciaSemConquistas`).
- Falha na verificação de parecidas mostra o erro e não adiciona a conquista.
- Testes: `tsc -b`, `npm run lint` e `vitest run` (367 testes) passando.

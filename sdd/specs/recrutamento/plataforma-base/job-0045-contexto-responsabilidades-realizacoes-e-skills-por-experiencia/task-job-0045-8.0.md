# Tarefa 8.0: Frontend: perfil, importação e migração com skills em tags

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

A tela do perfil edita os quatro blocos por experiência, com skills em tags, e permite importar um PDF ou migrar um perfil antigo revisando o resultado antes de salvar.

<requirements>
- Extrair o `EditorTags` (criar com Enter ou vírgula, excluir pelo botão da tag) do `EditorCompetencias`, sem mudar o comportamento atual dele.
- `PerfilPage` e `formulario-perfil.ts`: campos "Contexto", "Principais responsabilidades" (um item por linha), "Principais realizações" (o banco de conquistas) e "Skills" (tags).
- Perfil antigo: ao abrir, oferecer a migração, mostrar o rascunho e salvar só após a confirmação; itens gerados pela IA identificados até confirmar.
- Aviso de métricas e contextos que a IA pode ter estimado, na importação e na migração.
- Após salvar, informar as tecnologias incluídas pelas skills; as tecnologias gerais continuam como campo de texto.
- Rótulos associados, anúncio de tags criadas e removidas, foco devolvido após aplicar sugestão; tipos da API (`tipos.ts`, `schema.d.ts`, `http-api-client.ts`) atualizados.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 8.1 Escrever os testes do formulário, do `EditorTags` e da página (red).
- [x] 8.2 Extrair o `EditorTags` e adaptar o `EditorCompetencias` (green).
- [x] 8.3 Implementar os campos, a migração e a importação (green).
- [x] 8.4 Atualizar os tipos e o cliente HTTP (green).
- [x] 8.5 Refatorar e rodar o Vitest.

## Detalhes de Implementação

Techspec: "Visão Geral dos Componentes" (Frontend) e "Endpoints de API". PRD: RF 11 a 15 e 19.

Complexidade: high. Dependências: 3.0, 5.0.

## Critérios de Sucesso

- O usuário edita os quatro blocos e as skills e salva; a lista de tecnologias incluídas aparece.
- Importar ou migrar nunca grava sem confirmação.
- Os testes atuais do perfil e das competências continuam verdes.

## Testes da Tarefa

- [x] Vitest: `formulario-perfil`, `EditorTags`, `EditorCompetencias` (regressão) e `PerfilPage`.
- [x] Vitest do `http-api-client`.
- [x] Regressão: `npm test` em `frontend/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/EditorTags.tsx (novo)`
- `frontend/src/shared/formulario-curriculo/EditorCompetencias.tsx`
- `frontend/src/features/perfil/PerfilPage.tsx`
- `frontend/src/features/perfil/formulario-perfil.ts`
- `frontend/src/features/perfil/ConquistasDaExperiencia.tsx`
- `frontend/src/features/perfil/ImportarPerfilModal.tsx`
- `frontend/src/api/{tipos.ts,schema.d.ts,http-api-client.ts}`
- `frontend/src/test/fixtures.ts`

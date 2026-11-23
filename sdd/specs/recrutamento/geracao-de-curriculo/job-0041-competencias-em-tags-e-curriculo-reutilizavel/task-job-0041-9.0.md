# Tarefa 9.0: Reabrir o currículo depois de fechar a tela

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Permite editar um currículo adaptado depois de fechar ou recarregar a tela, por uma página de edição com rota própria e dois pontos de entrada: a lista de Currículos e o detalhe da candidatura.

<requirements>
- Rota `/curriculos-adaptados/:id` com a revisão em modo edição, carregando o conteúdo por `GET /curriculos-adaptados/{id}`.
- Lista de Currículos mostra os currículos adaptados com a ação "Editar".
- `DetalheCandidaturaModal` mostra "Editar currículo" quando a candidatura tem currículo adaptado vinculado.
- Salvar atualiza o PDF e permite baixá-lo.
- Id inexistente ou de outro perfil mostra mensagem de não encontrado.
- Os pontos de entrada seguem a proposta do PRD e podem ser revistos quando a questão em aberto 2 for decidida.
</requirements>

## Subtarefas

- [ ] 9.1 Testes da página de edição: carrega, edita, salva, baixa, não encontrado (red).
- [ ] 9.2 Testes de `CurriculosPage` e `DetalheCandidaturaModal` com a ação de editar (red).
- [ ] 9.3 Expor o vínculo candidatura e currículo adaptado na leitura da candidatura (backend, mínimo necessário) com teste.
- [ ] 9.4 Implementar a página, a rota e a ação nos dois pontos de entrada (green).
- [ ] 9.5 Rodar lint e tipos do frontend.

## Detalhes de Implementação

Techspec: "Componentes" (frontend). PRD: RF 11 e Questões em Aberto 2. Reaproveitar o modo edição da tarefa 8.0.

## Critérios de Sucesso

- Um currículo adaptado é reaberto após recarregar a página e após novo login, com o mesmo conteúdo.
- Candidaturas sem currículo adaptado não mostram a ação.

## Testes da Tarefa

- [ ] Testes de unidade (Vitest e Testing Library) e do backend tocado.
- [ ] Regressão: `frontend/src/features/curriculos/` e `frontend/src/features/candidaturas/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/curriculos/CurriculosPage.tsx`
- `frontend/src/features/candidaturas/DetalheCandidaturaModal.tsx`
- `frontend/src/features/curriculos-adaptados/` (novo)
- `frontend/src/app/` (rotas)
- `src/jobsync/entrypoints/api/routers/candidatura_router.py`

# Tarefa 7.0: Telas Vagas salvas (T7) e Candidaturas/Kanban (T9)

<critical>Ler os arquivos prd-job-0015.md e techspec-job-0015.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Entregar a gestão do funil: vagas capturadas pela extensão ou coladas, a conversão em candidatura e o Kanban de candidaturas.

- **Complexidade:** medium
- **Dependências:** 6.0 (atalhos para Ajustar e Analisar ATS)

<requirements>
- Vagas salvas: listar com `GET /v1/vagas` (primeira linha do texto como título, domínio da URL e data de captura) (RF8.1).
- Registrar vaga colada via `POST /v1/vagas` (RF8.2).
- Ver a descrição completa e avaliá-la com `POST /v1/vagas/avaliacoes` (RF8.3).
- Criar candidatura (empresa, cargo, currículo usado) via `POST /v1/candidaturas`, invalidando vagas e candidaturas (RF8.4).
- Atalhos para Ajustar para uma vaga e Analisar ATS já preenchidos (RF8.5).
- Kanban: colunas Aplicado, Entrevista, Oferta e Rejeitado com contagem (RF10.1). Rótulos pt-BR em mapa de apresentação.
- Mover por menu "Mover para" via `POST /v1/candidaturas/{id}/submissao` (RF10.2). Arrastar e soltar é opcional.
- Detalhe com histórico de status e currículo usado (RF10.3).
</requirements>

## Subtarefas

- [x] 7.1 Escrever os testes (red) e implementar a listagem e o registro manual em `features/vagas-salvas/`.
- [x] 7.2 Implementar o detalhe, a avaliação e os atalhos.
- [x] 7.3 Implementar o modal de criar candidatura.
- [x] 7.4 Escrever os testes (red) e implementar o Kanban em `features/candidaturas/`.
- [x] 7.5 Implementar o detalhe da candidatura com histórico.

## Detalhes de Implementação

Ver `prd-job-0015.md` → F8 e F10, e `techspec-job-0015.md` → "Modelos de Dados" (status do Kanban) e "Fluxo de dados" (invalidação de queries). Referência funcional: `_renderizar_vagas_capturadas` e `_renderizar_kanban` em `streamlit_app.py`.

## Critérios de Sucesso

- Uma vaga capturada pela extensão aparece na lista depois de recarregar.
- Criar candidatura tira a vaga da lista e coloca o cartão na coluna Aplicado.
- Mover um cartão persiste depois de recarregar e aparece no histórico.

## Testes da Tarefa

- [x] Testes de unidade: registrar vaga colada adiciona item à lista.
- [x] Testes de unidade: criar candidatura remove a vaga e invalida as duas queries.
- [x] Testes de unidade: Kanban mostra 4 colunas com contagem; mover chama a API e atualiza a coluna.
- [x] Testes de unidade: detalhe lista o histórico em ordem.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/vagas-salvas/` (novo)
- `frontend/src/features/candidaturas/` (novo)
- `src/jobsync/entrypoints/api/routers/vaga_router.py`
- `src/jobsync/entrypoints/api/routers/candidatura_router.py`
- `src/jobsync/entrypoints/api/schemas/candidatura.py`

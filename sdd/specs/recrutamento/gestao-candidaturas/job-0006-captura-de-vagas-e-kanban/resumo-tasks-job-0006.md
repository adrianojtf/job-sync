# Resumo de Tarefas de Implementação de Captura de Vagas e Kanban

## Tarefas

- [x] 1.0 Modelar entidades de domínio (Vaga, Candidatura, StatusCandidatura, TokenCaptura)
- [x] 2.0 Definir portas RepositorioVagaPort e RepositorioCandidaturaPort
- [x] 3.0 Estender RepositorioSqlite com as tabelas vaga, candidatura, token_captura + testes de integração (implementado como classes irmãs `RepositorioVagaSqlite`/`RepositorioCandidaturaSqlite` no mesmo módulo, para evitar colisão de nomes de método entre portas — ver docstring do módulo)
- [x] 4.0 Implementar use cases de vaga (CapturarVaga, ListarVagasCapturadas) com testes
- [x] 5.0 Implementar use cases de candidatura (CriarCandidatura, MoverCandidatura, ListarCandidaturasPorStatus) com testes
- [x] 6.0 Implementar ServidorCaptura (FastAPI) com o endpoint de captura + testes com TestClient
- [x] 7.0 Construir a extensão Chrome (manifest, content script, background script, popup do token) — arquivos criados e validados sintaticamente; carregamento e teste manual no Chrome real ficam pendentes para o usuário (ver Tarefa 9.0)
- [x] 8.0 Integrar o Kanban de candidaturas na UI Streamlit, com menu lateral e estilo inspirado no shadcn
- [x] 9.0 Validação manual end-to-end e execução da suíte completa de testes

## Dependências

- 1.0 deve ser concluída antes de 2.0.
- 2.0 deve ser concluída antes de 3.0.
- 3.0 deve ser concluída antes de 4.0 e 5.0 (podem ser feitas em paralelo entre si).
- 4.0 deve ser concluída antes de 6.0.
- 6.0 deve ser concluída antes de 7.0.
- 5.0 deve ser concluída antes de 8.0.
- 7.0 e 8.0 devem ser concluídas antes de 9.0.

## Entregáveis principais

- Entidades `Vaga`, `Candidatura` (com `StatusCandidatura`) e `TokenCaptura`, sem dependência de infraestrutura.
- Persistência estendida (SQLite) para vagas capturadas, candidaturas e tokens de captura, reaproveitando o banco da Fase 0.
- Servidor HTTP local (FastAPI) expondo um único endpoint de captura, autenticado por token opaco.
- Extensão de navegador Chrome capaz de capturar o texto de uma página e enviá-lo ao servidor de captura.
- Kanban de candidaturas (Aplicado/Entrevista/Oferta/Rejeitado) na UI Streamlit, organizado por um menu lateral (`st.sidebar`) e com estilo visual inspirado no shadcn (via CSS customizado, mantendo o Streamlit como stack).

## Nota de implementação

O modelo de domínio expõe `Candidatura.historico_status`, mas o schema aprovado para esta fase tem apenas 3 tabelas (`vaga`, `candidatura`, `token_captura`) — sem uma tabela dedicada de auditoria de histórico. Nesta fase, `historico_status` conterá apenas o registro da mudança de status mais recente (não um histórico completo), suficiente para os requisitos da Fase 2 e da Fase 4 (que só consome o status atual). Uma tabela de auditoria completa pode ser adicionada depois, se necessário.

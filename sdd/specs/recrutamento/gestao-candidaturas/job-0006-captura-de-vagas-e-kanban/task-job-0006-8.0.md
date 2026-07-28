# Tarefa 8.0: Integrar Kanban de candidaturas na UI Streamlit, com menu lateral e estilo inspirado no shadcn

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Reorganizar `ui/app_streamlit.py` em duas áreas navegáveis por um menu lateral (`st.sidebar`) — "Adaptar Currículo" (fluxo já existente das Fases 0/1) e "Vagas & Candidaturas" (novo Kanban) — e aplicar um tema visual inspirado no shadcn/ui via CSS customizado, mantendo o Streamlit como stack (decisão já validada com o usuário: sem migração para React).

<requirements>
- Menu lateral com pelo menos duas opções de navegação, usando `st.sidebar.radio` ou equivalente nativo do Streamlit.
- Página "Vagas & Candidaturas": lista de vagas capturadas não convertidas (com botão "criar candidatura"), e o Kanban com 4 colunas (`st.columns`) mostrando as candidaturas via `ListarCandidaturasPorStatus`, com botões para mover entre status.
- Estilo shadcn: injetar CSS customizado (via `st.markdown(..., unsafe_allow_html=True)`) aproximando cantos arredondados, paleta neutra e cards com borda sutil — sem introduzir dependência de bibliotecas React/JS externas.
- Fluxo existente de adaptação de currículo (Fases 0/1) continua funcionando sem regressão, apenas realocado para sua própria página no menu lateral — complexidade: high.
</requirements>

## Subtarefas

- [x] 8.1 Introduzir navegação por `st.sidebar` com as páginas "Adaptar Currículo" e "Vagas & Candidaturas".
- [x] 8.2 Mover o fluxo de adaptação existente (Fases 0/1) para a página "Adaptar Currículo", sem alterar seu comportamento.
- [x] 8.3 Construir a página "Vagas & Candidaturas": lista de vagas capturadas + formulário de criação de candidatura (escolhendo currículo salvo, empresa, cargo).
- [x] 8.4 Construir o Kanban com 4 colunas e botões de mover status, consumindo `ListarCandidaturasPorStatus` e `MoverCandidatura`.
- [x] 8.5 Injetar CSS customizado (bloco `<style>` via `st.markdown`) aplicando estética inspirada no shadcn (cantos arredondados, cards com borda sutil, paleta neutra).

## Detalhes de Implementação

Consultar a seção "Visão Geral dos Componentes" (fluxo de dados do Kanban) de `techspec-job-0006.md`. A extensão de navegador (Tarefa 7.0) e o `ServidorCaptura` (Tarefa 6.0) alimentam a lista de "vagas capturadas"; esta tarefa é só a camada de apresentação/consumo desses dados já persistidos.

## Critérios de Sucesso

- Usuário navega entre "Adaptar Currículo" e "Vagas & Candidaturas" pelo menu lateral sem perder o estado de login.
- Vaga capturada pela extensão aparece na lista e pode virar uma candidatura.
- Candidatura pode ser movida entre as 4 colunas do Kanban.
- Estilo visual aplicado sem quebrar nenhum componente nativo do Streamlit.

## Testes da Tarefa

- [x] Teste manual: navegar entre as duas páginas do menu lateral.
- [x] Teste manual: criar candidatura a partir de uma vaga e movê-la entre colunas do Kanban.
- [x] Teste manual: confirmar que o fluxo de adaptação de currículo (Fases 0/1) continua funcionando normalmente na sua página.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `ui/app_streamlit.py`

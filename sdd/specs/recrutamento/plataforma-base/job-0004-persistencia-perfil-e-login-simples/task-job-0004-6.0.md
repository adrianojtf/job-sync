# Tarefa 6.0: Integrar login e biblioteca de currículos na UI Streamlit

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Conectar todos os use cases das Tarefas 4.0 e 5.0 à interface Streamlit já existente (`ui/app_streamlit.py`), adicionando a tela de entrada por identificador e a biblioteca de currículos, sem alterar o fluxo de adaptação já existente além de permitir que ele receba um currículo salvo como entrada alternativa ao upload.

<requirements>
- Ao abrir a aplicação, o usuário deve ser solicitado a informar um identificador antes de acessar qualquer outra funcionalidade.
- O identificador deve ficar guardado em `st.session_state` pelo restante da sessão.
- A biblioteca de currículos deve permitir upload, listagem, seleção (como entrada para adaptação) e remoção.
- O fluxo de adaptação existente (`AdaptarCurriculoParaVaga`) não deve ser modificado — apenas a origem do `pdf_bytes` passa a poder vir da biblioteca — complexidade: medium.
</requirements>

## Subtarefas

- [ ] 6.1 Adicionar tela de entrada por identificador no início de `ui/app_streamlit.py`, usando `EntrarOuCriarPerfil`.
- [ ] 6.2 Adicionar seção de biblioteca de currículos: upload (`SalvarCurriculo`), listagem (`ListarCurriculosSalvos`), remoção (`RemoverCurriculoSalvo`).
- [ ] 6.3 Permitir que o usuário escolha entre "enviar novo PDF" ou "selecionar currículo salvo" como entrada para o formulário de adaptação já existente.
- [ ] 6.4 Exibir mensagem clara quando o limite de 10 currículos for atingido (retorno de erro da Tarefa 5.0).

## Detalhes de Implementação

Consultar a seção "Visão Geral dos Componentes" (fluxo de dados) de `techspec-job-0004.md`. Instanciar `RepositorioSqlite` uma vez por sessão/processo e injetá-lo nos use cases, seguindo o padrão de composição já usado para os adapters existentes em `ui/app_streamlit.py`.

## Critérios de Sucesso

- Usuário consegue entrar com um identificador, fazer upload de um currículo, fechar e reabrir a aplicação, e encontrar o currículo salvo na biblioteca.
- Fluxo de adaptação existente continua funcionando sem regressão, seja com upload novo ou com currículo salvo selecionado.

## Testes da Tarefa

- [ ] Teste manual: primeiro acesso cria perfil e biblioteca vazia.
- [ ] Teste manual: upload, fechar app, reabrir, currículo ainda aparece na biblioteca.
- [ ] Teste manual: 11º upload é bloqueado com mensagem clara.
- [ ] Teste manual: seleção de currículo salvo alimenta corretamente o fluxo de adaptação existente.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `ui/app_streamlit.py`

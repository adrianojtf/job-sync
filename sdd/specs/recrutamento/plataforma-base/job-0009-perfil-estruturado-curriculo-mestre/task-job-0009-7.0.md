# Tarefa 7.0: UI — página "Meu Perfil"

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Construir a nova página "Meu Perfil" na UI Streamlit: formulário estruturado (dados pessoais, resumo, experiências, formação, certificações, idiomas, tecnologias, com suporte a múltiplas entradas dinâmicas), opção de importar de um PDF para pré-preencher, e botão salvar.

<requirements>
- Novo item de menu lateral "Meu Perfil".
- Campos: nome completo, email, LinkedIn (URL), resumo profissional (`st.text_area`).
- Experiências, formação, certificações e idiomas: listas editáveis (adicionar/remover entradas), usando `st.session_state` para rastrear o estado entre reruns (padrão comum do Streamlit para listas dinâmicas).
- Tecnologias: campo de texto simples, tecnologias separadas por vírgula, convertidas em `tuple[str, ...]` ao salvar.
- Opção "Importar de um PDF" (upload novo ou escolher da biblioteca existente, Fase 0): ao importar, chama `ImportarPerfilDePdf`, e os campos do formulário são pré-preenchidos com o resultado — usuário pode editar livremente antes de salvar.
- Botão "Salvar perfil": chama `SalvarPerfilEstruturado`.
- Ao abrir a página, se já existir um perfil salvo (`BuscarPerfilEstruturado`), os campos do formulário vêm pré-preenchidos com os dados salvos (edição, não só criação).
- Complexidade: high (formulário com múltiplas listas dinâmicas é a parte mais trabalhosa desta fase).
</requirements>

## Subtarefas

- [ ] 7.1 Adicionar a composição (`@st.cache_resource`) do repositório e dos use cases de perfil estruturado.
- [ ] 7.2 Construir os campos de dados pessoais + resumo profissional, pré-preenchidos se já existir perfil salvo.
- [ ] 7.3 Construir a seção de experiências (lista dinâmica: adicionar/remover, campos empresa/cargo/período/descrição).
- [ ] 7.4 Construir a seção de formação acadêmica (lista dinâmica: instituição/curso/período).
- [ ] 7.5 Construir a seção de certificações (lista dinâmica: nome/instituição/ano) e idiomas (lista dinâmica: idioma/nível).
- [ ] 7.6 Construir o campo de tecnologias e o botão "Salvar perfil".
- [ ] 7.7 Construir a opção "Importar de um PDF", pré-preenchendo o estado do formulário com o resultado de `ImportarPerfilDePdf`.

## Detalhes de Implementação

Consultar a seção "Sequenciamento de Desenvolvimento" (item 7) de `techspec-job-0009.md`. Reaproveitar o estilo CSS shadcn já aplicado (`_injetar_estilo_shadcn`) e o padrão de listas dinâmicas via `st.session_state` (não existe um exemplo direto no código atual — usar uma lista de dicts em `st.session_state`, com `st.button` de "Adicionar" incrementando a lista e `st.rerun()` para refletir).

## Critérios de Sucesso

- A página "Meu Perfil" permite criar, editar e salvar um perfil completo com múltiplas entradas em cada lista.
- Importar de um PDF pré-preenche o formulário, que continua editável antes de salvar.
- Reabrir a página depois de salvar mostra os dados já preenchidos.

## Testes da Tarefa

- [ ] Validação manual: preencher um perfil do zero com múltiplas experiências/formações, salvar, e conferir que reabrir a página mostra os dados salvos.
- [ ] Validação manual: importar de um PDF real, conferir que os campos aparecem pré-preenchidos e editáveis, editar algo e salvar.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/ui/app_streamlit.py`

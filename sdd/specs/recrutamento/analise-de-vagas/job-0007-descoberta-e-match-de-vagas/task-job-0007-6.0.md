# Tarefa 6.0: Integrar menu lateral "Vagas" na UI Streamlit

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Adicionar um novo item de menu lateral, "Vagas", separado de "Adaptar Currículo", "Analisar ATS" e "Vagas & Candidaturas" (Kanban, Fase 2). A tela permite buscar vagas por termo, escolher um currículo salvo como referência, e ver a lista de resultados ordenada por score de match.

<requirements>
- Novo item `st.sidebar` "Vagas", ao lado dos três já existentes.
- Campo de texto para o termo de busca (ex: "engenheiro de software backend").
- Seletor de currículo salvo (reaproveitando `ListarCurriculosSalvos`, Fase 0, já existente).
- Ao buscar, chama `DescobrirVagasComMatch.executar(termo, pdf_curriculo)` e exibe a lista ordenada por score.
- Cada item da lista mostra: título, empresa, fonte, score, e um detalhe expansível com requisitos batidos/faltantes (reaproveitando o componente visual já usado no ATS Score, Fase 1).
- Indicação visual quando `descricao_incompleta=True` (resultado do Google Custom Search sem extração completa).
- Falha de uma fonte não deve impedir a exibição das vagas das demais.
- Complexidade: medium.
</requirements>

## Subtarefas

- [ ] 6.1 Adicionar a composição (`@st.cache_resource`) do `DescobrirVagasComMatch` com os cinco buscadores.
- [ ] 6.2 Criar a página "Vagas" com busca por termo + seletor de currículo salvo.
- [ ] 6.3 Renderizar a lista de resultados ordenada por score, com detalhe expansível de requisitos.
- [ ] 6.4 Exibir indicação visual para vagas com `descricao_incompleta=True`.

## Detalhes de Implementação

Consultar a seção "Sequenciamento de Desenvolvimento" de `techspec-job-0007.md`. Reaproveitar o estilo CSS shadcn já aplicado (`_injetar_estilo_shadcn`).

## Critérios de Sucesso

- A página "Vagas" aparece no menu lateral, busca nas cinco fontes e exibe os resultados ordenados por score, sem travar quando uma fonte falha.

## Testes da Tarefa

- [ ] Validação manual: buscar um termo real e conferir que a lista aparece ordenada por score, com detalhe de requisitos.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/ui/app_streamlit.py`

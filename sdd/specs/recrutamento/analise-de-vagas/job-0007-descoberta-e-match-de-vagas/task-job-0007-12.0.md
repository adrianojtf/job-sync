# Tarefa 12.0: Seletor de período na UI "Vagas" + exibir data de publicação

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Adicionar um seletor de período ("7 dias" / "15 dias" / "30 dias" / "Qualquer período") na página "Vagas", repassado como `dias_maximo` ao chamar `DescobrirVagasComMatch.executar`, e exibir a data de publicação (ou "data desconhecida") em cada vaga da lista de resultados.

<requirements>
- Seletor (`st.selectbox`) com as opções "Qualquer período", "7 dias", "15 dias", "30 dias", mapeadas para `dias_maximo = None, 7, 15, 30` respectivamente.
- O valor escolhido é passado para `use_case.executar(termo, pdf_curriculo, dias_maximo)`.
- Em `_renderizar_vaga_descoberta`: exibir a data de publicação formatada (ex: "Publicada em 20/07/2026") quando `vaga.data_publicacao` não for `None`; caso contrário, exibir "Data de publicação desconhecida".
- Complexidade: low.
</requirements>

## Subtarefas

- [ ] 12.1 Adicionar o seletor de período na página "Vagas" (`_pagina_vagas`), próximo aos demais campos de busca.
- [ ] 12.2 Repassar o valor escolhido como `dias_maximo` na chamada ao use case.
- [ ] 12.3 Exibir a data de publicação (ou "desconhecida") em `_renderizar_vaga_descoberta`.

## Detalhes de Implementação

Consultar a seção "Sequenciamento de Desenvolvimento" (item 9, atualizado) de `techspec-job-0007.md`.

## Critérios de Sucesso

- O seletor de período aparece na UI e influencia os resultados retornados.
- Cada vaga exibida mostra a data de publicação ou a indicação de que é desconhecida.

## Testes da Tarefa

- [ ] Validação manual: aplicar um filtro de período (ex: 7 dias) e conferir que vagas fora da janela (com data conhecida) não aparecem, mas vagas de fonte sem data (Google Custom Search) continuam aparecendo.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/ui/app_streamlit.py`

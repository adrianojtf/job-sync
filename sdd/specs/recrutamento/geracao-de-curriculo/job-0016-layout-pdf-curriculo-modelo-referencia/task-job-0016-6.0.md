# Tarefa 6.0: GeradorPdfClient — formação, certificações e idiomas

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Aplicar o padrão do modelo às seções finais: instituição e período na mesma linha, curso/grau em itálico azul na linha abaixo, e idiomas um por linha.

<requirements>
- Formação: instituição em Bold preto + período em `#595959` à direita; curso e grau em Italic `#1F3864` na linha abaixo (RF 25).
- Certificações: mesmo padrão de formação (RF 26).
- Idiomas: uma linha por idioma, idioma em negrito e nível em regular (RF 27).
- Reaproveitar `InterpretadorExperiencias` e o componente de linha empresa + período da tarefa 5.0 (DRY).
- Formatos antigos de formação (ex.: `Education: Estácio, Jun 2022 - Jun 2024, Associate Degree ...`) continuam gerando PDF válido sem perda de texto.
- Revisar se `_negritar_formacao` e funções associadas continuam necessárias; remover o que ficar sem uso e atualizar os testes correspondentes.
</requirements>

## Subtarefas

- [ ] 6.1 Escrever testes com `pdfplumber` para formação, certificações e idiomas (red).
- [ ] 6.2 Implementar formação e certificações reaproveitando o componente da tarefa 5.0.
- [ ] 6.3 Implementar idiomas.
- [ ] 6.4 Revisar código antigo de formação e testes associados.

## Detalhes de Implementação

Consultar em `techspec-job-0016.md` a seção "Regras de renderização" (item Formação/Certificações).

## Critérios de Sucesso

- Seção de formação gerada com o conteúdo do modelo fica igual ao modelo.
- Nenhum texto da entrada some do PDF.

## Testes da Tarefa

- [ ] `Estácio` em `Carlito-Bold` e `Jun 2022 - Jun 2024` alinhado à direita em `#595959`.
- [ ] `Systems Analysis and Development - Associate Degree` em `Carlito-Italic` `#1F3864`.
- [ ] Certificação com nome e ano na mesma linha.
- [ ] Idiomas: uma linha por idioma, idioma em negrito.
- [ ] Formato antigo de formação gera PDF válido com todo o texto.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/gerador_pdf_client.py`
- `src/jobsync/curriculo/adapters/pdf/interpretador_experiencias.py`
- `src/jobsync/tests/curriculo/test_gerador_pdf_client.py`

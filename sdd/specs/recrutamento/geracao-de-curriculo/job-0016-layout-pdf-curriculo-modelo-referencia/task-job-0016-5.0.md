# Tarefa 5.0: GeradorPdfClient — experiências com empresa/período, cargo, tópicos e contexto

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Renderizar a seção de experiências igual ao modelo, com foco nos tópicos separados por `-`: marcador `●`, recuo e quebra de linha alinhada ao texto. Empresa e período ficam na mesma linha, com o período à direita.

<requirements>
- Usar `InterpretadorExperiencias` (tarefa 2.0) para obter os blocos.
- Empresa em Bold 11,5 pt preto à esquerda; período em Regular 10,5 pt `#595959` à direita, terminando em x ≈ 513 pt, via `Table` sem padding (RF 16).
- Bloco sem período mostra só a empresa, sem erro (RF 24).
- Cabeçalho `Cargo — Empresa (Período)`: empresa em negrito com o período à direita e cargo em itálico azul-marinho na linha abaixo (RF 32).
- A linha de contexto é desenhada com o rótulo que veio no texto (RF 34), em Carlito Italic `#595959`.
- Remover `_estilo_contexto` e `_eh_linha_de_contexto` do JOB-0035, que ficam substituídos pelo estilo e pelo interpretador.
- Atualizar os testes do JOB-0035 sobre o contexto em `test_gerador_pdf_client.py`, trocando `Helvetica-Oblique` e `#666666` por `Carlito-Italic` e `#595959` e mantendo as demais asserções.
- Cargo em Italic 10,5 pt `#1F3864` na linha abaixo (RF 17).
- Tópicos com `Paragraph(..., bulletText="●")`, `bulletIndent=18`, `leftIndent=36`, recuo pendente e `spaceAfter` entre tópicos (RF 18 a 20).
- Contexto em Italic 10,5 pt `#595959`, após os tópicos (RF 21).
- Espaço vertical entre experiências (RF 22).
- Blocos sem tópicos ou sem contexto não deixam espaço vazio (RF 23).
- `keepWithNext` na empresa, no cargo, no título e na linha da seção, evitando cabeçalho órfão (sem `KeepTogether` aninhado, que empurra o conteúdo para a página seguinte).
- Espaçamentos e margem superior medidos no modelo (ver techspec, "Espaçamentos medidos no modelo").
- Ordem do texto extraído: empresa → período → cargo → tópicos → contexto (ATS).
- Remover o código antigo de experiências que deixar de ser usado (`_negritar_experiencia`, `_formatar_conteudo_experiencias`, `_separar_blocos_experiencias`), se não houver outro uso.
</requirements>

## Subtarefas

- [x] 5.1 Escrever testes com `pdfplumber` para posição, fonte e cor de cada parte (red).
- [x] 5.2 Implementar a linha empresa + período com `Table`.
- [x] 5.3 Implementar cargo, tópicos e contexto.
- [x] 5.4 Implementar espaçamento entre blocos e `keepWithNext`.
- [x] 5.5 Reescrever os testes antigos de experiências para a nova saída.
- [x] 5.6 Remover código morto e refatorar.

## Detalhes de Implementação

Consultar em `techspec-job-0016.md`:
- "Regras de renderização" (empresa + período, tópicos, contexto, bloco de experiência).
- "Abordagem de Testes" (lista de testes existentes que mudam de expectativa).

## Critérios de Sucesso

- Gerando o PDF com o conteúdo do modelo, a seção de experiências fica visualmente igual ao modelo.
- 100% dos tópicos `-` da entrada aparecem como itens com `●` no PDF.
- Nenhum texto da entrada some do PDF.

## Testes da Tarefa

- [x] Tópico `-` gera `●` com x ≈ 63 pt.
- [x] Linha de continuação de tópico longo começa em x ≈ 81 pt.
- [x] Período com x1 ≈ 513 pt e cor `#595959`.
- [x] Empresa em `Carlito-Bold` 11,5 pt.
- [x] Cargo em `Carlito-Italic` com cor `#1F3864`.
- [x] Contexto em `Carlito-Italic` com cor `#595959`.
- [x] Experiência só com contexto e experiência sem período geram PDF válido.
- [x] Cabeçalho `Cargo — Empresa (Período)` gera empresa em `Carlito-Bold`, período à direita e cargo na linha abaixo em `Carlito-Italic` `#1F3864`.
- [x] Contexto exibe o rótulo `Context:` ou `Contexto:` no PDF.
- [x] Ordem do texto extraído: empresa → período → cargo → tópicos → contexto.
- [x] Testes antigos substituídos por testes sobre o PDF gerado: os 3 de negrito e espaçamento do JOB-0002 e os 7 de contexto do JOB-0035 (mesmas asserções de comportamento, com `Carlito-Italic` e `#595959`).
- [x] Ritmo vertical (títulos, tecnologias, tópicos, contexto e espaço entre blocos) a menos de 1 pt do modelo.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/gerador_pdf_client.py`
- `src/jobsync/curriculo/adapters/pdf/interpretador_experiencias.py`
- `src/jobsync/curriculo/adapters/pdf/estilo_curriculo_pdf.py`
- `src/jobsync/tests/curriculo/test_gerador_pdf_client.py`

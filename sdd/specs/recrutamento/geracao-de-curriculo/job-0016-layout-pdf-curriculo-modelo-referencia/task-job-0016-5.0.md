# Tarefa 5.0: GeradorPdfClient — experiências com empresa/período, cargo, tópicos e contexto

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Renderizar a seção de experiências igual ao modelo, com foco nos tópicos separados por `-`: marcador `●`, recuo e quebra de linha alinhada ao texto. Empresa e período ficam na mesma linha, com o período à direita.

<requirements>
- Usar `InterpretadorExperiencias` (tarefa 2.0) para obter os blocos.
- Empresa em Bold 11,5 pt preto à esquerda; período em Regular 10,5 pt `#595959` à direita, terminando em x ≈ 513 pt, via `Table` sem padding (RF 16).
- Bloco sem período mostra só a empresa, sem erro (RF 24).
- Cargo em Italic 10,5 pt `#1F3864` na linha abaixo (RF 17).
- Tópicos com `Paragraph(..., bulletText="●")`, `bulletIndent=18`, `leftIndent=36`, recuo pendente e `spaceAfter` entre tópicos (RF 18 a 20).
- Contexto em Italic 10,5 pt `#595959`, após os tópicos (RF 21).
- Espaço vertical entre experiências (RF 22).
- Blocos sem tópicos ou sem contexto não deixam espaço vazio (RF 23).
- `KeepTogether` para cabeçalho + cargo + primeiro item, evitando cabeçalho órfão.
- Ordem do texto extraído: empresa → período → cargo → tópicos → contexto (ATS).
- Remover o código antigo de experiências que deixar de ser usado (`_negritar_experiencia`, `_formatar_conteudo_experiencias`, `_separar_blocos_experiencias`), se não houver outro uso.
</requirements>

## Subtarefas

- [ ] 5.1 Escrever testes com `pdfplumber` para posição, fonte e cor de cada parte (red).
- [ ] 5.2 Implementar a linha empresa + período com `Table`.
- [ ] 5.3 Implementar cargo, tópicos e contexto.
- [ ] 5.4 Implementar espaçamento entre blocos e `KeepTogether`.
- [ ] 5.5 Reescrever os testes antigos de experiências para a nova saída.
- [ ] 5.6 Remover código morto e refatorar.

## Detalhes de Implementação

Consultar em `techspec-job-0016.md`:
- "Regras de renderização" (empresa + período, tópicos, contexto, bloco de experiência).
- "Abordagem de Testes" (lista de testes existentes que mudam de expectativa).

## Critérios de Sucesso

- Gerando o PDF com o conteúdo do modelo, a seção de experiências fica visualmente igual ao modelo.
- 100% dos tópicos `-` da entrada aparecem como itens com `●` no PDF.
- Nenhum texto da entrada some do PDF.

## Testes da Tarefa

- [ ] Tópico `-` gera `●` com x ≈ 63 pt.
- [ ] Linha de continuação de tópico longo começa em x ≈ 81 pt.
- [ ] Período com x1 ≈ 513 pt e cor `#595959`.
- [ ] Empresa em `Carlito-Bold` 11,5 pt.
- [ ] Cargo em `Carlito-Italic` com cor `#1F3864`.
- [ ] Contexto em `Carlito-Italic` com cor `#595959`.
- [ ] Experiência só com contexto e experiência sem período geram PDF válido.
- [ ] Ordem do texto extraído: empresa → período → cargo → tópicos → contexto.
- [ ] Testes reescritos: `test_formatar_experiencias_com_cabecalho_e_posicao`, `test_nao_aplica_negrito_em_descricao_de_experiencia`, `test_adiciona_espacamento_extra_entre_blocos_de_experiencia`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/gerador_pdf_client.py`
- `src/jobsync/curriculo/adapters/pdf/interpretador_experiencias.py`
- `src/jobsync/curriculo/adapters/pdf/estilo_curriculo_pdf.py`
- `src/jobsync/tests/curriculo/test_gerador_pdf_client.py`

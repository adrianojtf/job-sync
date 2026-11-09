# Tarefa 4.0: GeradorPdfClient — página, cabeçalho, títulos de seção, tecnologias e perfil

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Aplicar o novo layout à parte superior do currículo: margens da página, cabeçalho centralizado com link do LinkedIn, títulos de seção em caixa alta com linha azul-marinho, uma categoria de tecnologia por linha e parágrafo de perfil.

<requirements>
- Página Carta com margens laterais de 45 pt (RF 1).
- `GeradorPdfClient` deve receber `EstiloCurriculoPdf` e `RegistradorFontesPdf` por injeção opcional no construtor, com padrão interno (mantém compatibilidade com `dependencies.py` e `streamlit_app.py`).
- Nome em caixa alta, centralizado, Carlito Bold 16 pt, `#1F3864` (RF 4).
- Contato centralizado, 10 pt, `#595959`, LinkedIn como link clicável azul sublinhado (RF 5 e 6).
- Sem linha divisória logo abaixo do cabeçalho (RF 7).
- Título de seção em caixa alta, Bold 11 pt, `#1F3864`, com linha de 0,75 pt `#1F3864` em toda a largura (RF 8 a 11).
- Tecnologias: um `Paragraph` por categoria, rótulo em negrito, sem marcador; entrada em linha única com várias categorias deve ser quebrada antes de cada rótulo conhecido (RF 12 a 14).
- Perfil: parágrafo 10,5 pt preto, entrelinha 12,8 pt (RF 15).
- Reaproveitar `_negritar_categorias_tecnologia` e `_escape_text`.
- A porta `GeradorPdfPort` não muda.
</requirements>

## Subtarefas

- [ ] 4.1 Escrever testes que geram o PDF via `gerar()` e inspecionam com `pdfplumber` (red).
- [ ] 4.2 Injetar estilo e registrador de fontes no construtor.
- [ ] 4.3 Implementar margens e cabeçalho com link.
- [ ] 4.4 Implementar títulos de seção com linha.
- [ ] 4.5 Implementar a seção de tecnologias (uma linha por categoria + quebra de linha única).
- [ ] 4.6 Implementar a seção de perfil.
- [ ] 4.7 Ajustar testes existentes de tecnologias que dependam da estrutura antiga.

## Detalhes de Implementação

Consultar em `techspec-job-0016.md`:
- "Regras de renderização" (cabeçalho, título de seção, tecnologias).
- Tabela de medidas em "Visão Geral dos Componentes".

## Critérios de Sucesso

- Topo do PDF gerado, comparado com o modelo, tem as mesmas fontes, cores, alinhamentos e linhas.
- Testes antigos de ênfase em tecnologias (JOB-0002/0003) continuam verdes.

## Testes da Tarefa

- [ ] Nome em caixa alta, centralizado, `Carlito-Bold` 16 pt, cor `#1F3864`.
- [ ] Anotação de link do LinkedIn presente na página.
- [ ] Título `TECHNICAL SKILLS` em caixa alta, com linha horizontal abaixo.
- [ ] Tecnologias em várias linhas geram uma linha por categoria no PDF.
- [ ] Tecnologias em linha única com várias categorias geram uma linha por categoria.
- [ ] Ambiente sem fontes Carlito ainda gera PDF válido.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/gerador_pdf_client.py`
- `src/jobsync/curriculo/adapters/pdf/estilo_curriculo_pdf.py`
- `src/jobsync/curriculo/adapters/pdf/registrador_fontes_pdf.py`
- `src/jobsync/tests/curriculo/test_gerador_pdf_client.py`
- `src/jobsync/entrypoints/api/dependencies.py` (referência: instanciação)
- `src/jobsync/entrypoints/streamlit_app.py` (referência: instanciação)

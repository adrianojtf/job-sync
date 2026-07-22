# Tarefa 3.0: Implementar localização e agrupamento visual no gerador PDF

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar no `GeradorPdfReportLab` a tradução dos rótulos de seções e categorias de tecnologia, além do agrupamento visual das categorias conforme o idioma selecionado.

<requirements>
- Traduzir os títulos de seção exibidos no PDF com base no idioma alvo.
- Traduzir ou normalizar os rótulos de categorias de tecnologia na seção de tecnologias.
- Preservar o conteúdo factual do currículo e manter o destaque visual existente.
</requirements>

## Subtarefas

- [ ] 3.1 Integrar a camada de localização ao `GeradorPdfReportLab` para resolver textos de seções e categorias.
- [ ] 3.2 Ajustar o layout da seção de tecnologias para agrupar visualmente as categorias e os itens em português e inglês.
- [ ] 3.3 Validar que o conteúdo factual do currículo permanece intacto e que a renderização não quebra em entradas sem categorias explícitas.

## Detalhes de Implementação

Consultar `prd-job-0003.md` e `techspec-job-0003.md` para alinhar a organização esperada do PDF, os rótulos necessários e os cenários de fallback e renderização.

## Critérios de Sucesso

- Os rótulos de seção e de categorias aparecem no idioma correto.
- As categorias são apresentadas de forma estruturada e consistente.
- O PDF continua sendo gerado sem regressões para conteúdo já existente.

## Testes da Tarefa

- [ ] Testes de unidade para renderização de seções e categorias em pt/en.
- [ ] Testes de regressão para conteúdo sem categorias explícitas.

## Arquivos relevantes

- `infrastructure/pdf/gerador_pdf_reportlab.py`
- `tests/test_gerador_pdf.py`

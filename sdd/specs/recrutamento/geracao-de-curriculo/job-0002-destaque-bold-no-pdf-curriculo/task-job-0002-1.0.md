# Tarefa 1.0: Refatorar o adapter de geração de PDF ReportLab para suportar formatação inline de ênfase

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Refatorar o adapter `GeradorPdfReportLab` para extrair um helper de formatação de texto que aplica markup `<b>...</b>` compatível com ReportLab apenas aos rótulos e cabeçalhos destacados. O objetivo é manter o fluxo de geração de PDF existente enquanto habilita a lógica de ênfase necessária para a correção de formato.

<requirements>
- Implementar um helper interno para aplicar ênfase inline compatível com ReportLab.
- Integrar o helper ao processo de montagem de conteúdo antes de criar `Paragraph`.
- Preservar o texto original de `secao.conteudo` e evitar alterações no modelo de domínio.
</requirements>

## Subtarefas

- [ ] 1.1 Criar helper `_aplicar_enfase` em `infrastructure/pdf/gerador_pdf_reportlab.py`
- [ ] 1.2 Aplicar o helper antes de criar os objetos `Paragraph` no método de formatação de conteúdo
- [ ] 1.3 Confirmar que a refatoração não altera o conteúdo normal das descrições de experiência, tecnologias e formação

## Detalhes de Implementação

Referenciar o `techspec-job-0002.md` para entender a abordagem conservadora de formatação inline e garantir compatibilidade com ReportLab. A implementação deve permanecer dentro do adapter de PDF e não deve criar novos modelos de domínio.

## Critérios de Sucesso

- [ ] O helper de ênfase é responsável apenas por transformar strings para markup ReportLab.
- [ ] O fluxo de geração de PDF continua funcionando para currículos existentes.
- [ ] O texto não destacado permanece inalterado.

## Testes da Tarefa

- [ ] Criar um teste unitário que invoque `_formatar_conteudo` ou o helper de ênfase diretamente com exemplos de texto.
- [ ] Validar que o helper retorna markup `<b>...</b>` apenas onde esperado.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/geracao-de-curriculo/job-0002-destaque-bold-no-pdf-curriculo/prd-job-0002.md`
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0002-destaque-bold-no-pdf-curriculo/techspec-job-0002.md`
- `infrastructure/pdf/gerador_pdf_reportlab.py`

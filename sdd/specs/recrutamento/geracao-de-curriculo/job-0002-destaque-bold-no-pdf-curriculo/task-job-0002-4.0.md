# Tarefa 4.0: Criar testes de unidade que validem a geração de PDF e o markup de ênfase

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar ou atualizar o conjunto de testes que valida a implementação da ênfase em negrito e a geração de PDF no adapter `GeradorPdfReportLab`, conforme as regras definidas no PRD e na Tech Spec.

<requirements>
- Adicionar testes unitários para a função de formatação de conteúdo do adapter de PDF.
- Verificar que o markup de negrito é aplicado corretamente nas seções de Tecnologias, Experiências e Formação.
- Verificar que a geração do PDF retorna bytes válidos e compatíveis com ReportLab.
</requirements>

## Subtarefas

- [ ] 4.1 Adicionar testes para formatação de categorias de tecnologia.
- [ ] 4.2 Adicionar testes para formatação de cabeçalhos de experiência e posição.
- [ ] 4.3 Adicionar testes para formatação de títulos de formação.
- [ ] 4.4 Adicionar teste de geração de PDF que confirma bytes de saída válidos.

## Detalhes de Implementação

Use `tests/test_gerador_pdf.py` como base e estenda o caso de teste existente com novos exemplos de conteúdo. O objetivo é garantir que a implementação esteja coberta por testes e que a saída de PDF continue válida.

## Critérios de Sucesso

- [ ] Há cobertura para as regras de ênfase nas três seções principais.
- [ ] O fluxo de geração de PDF não quebra com os novos testes.
- [ ] Os testes fornecem falhas claras caso a lógica de formatação seja alterada inadvertidamente.

## Testes da Tarefa

- [ ] Executar `pytest` e validar que os testes relacionados a `GeradorPdfReportLab` passam.
- [ ] Confirmar que o helper de formatação lida corretamente com texto sem ênfase necessária.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/geracao-de-curriculo/job-0002-destaque-bold-no-pdf-curriculo/prd-job-0002.md`
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0002-destaque-bold-no-pdf-curriculo/techspec-job-0002.md`
- `tests/test_gerador_pdf.py`

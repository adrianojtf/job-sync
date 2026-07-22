# Tarefa 3.0: Ajustar espaçamento entre blocos de experiência e preservar o layout existente

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Aprimorar o adapter de PDF para inserir espaçamento visual adicional entre cada bloco de experiência no currículo, melhorando a leitura sem quebrar o layout atual ou alterar o conteúdo subjacente.

<requirements>
- Inserir uma linha em branco ou espaçamento adicional entre blocos de experiência.
- Preservar o estilo de parágrafos e bullets existentes.
- Manter compatibilidade com o mecanismo ReportLab e o layout atual do PDF.
</requirements>

## Subtarefas

- [ ] 3.1 Identificar blocos de experiência no conteúdo do currículo.
- [ ] 3.2 Inserir espaçamento extra entre cada experiência processada.
- [ ] 3.3 Validar que a formatação de bullets e parágrafos não seja afetada.

## Detalhes de Implementação

O `techspec-job-0002.md` especifica que a separação visual entre experiências deve melhorar a leitura cronológica. Ajuste o processamento de conteúdo para tratar cada bloco de experiência como um grupo distinto e adicionar espaçamento extra somente entre blocos.

## Critérios de Sucesso

- [ ] Os blocos de experiência são separados por espaçamento adicional no PDF.
- [ ] O restante do currículo mantém o layout e o estilo existentes.
- [ ] Não há quebra de renderização causada pela inserção de espaçamentos extras.

## Testes da Tarefa

- [ ] Criar ou estender testes para verificar espaçamento adicional entre blocos de experiência.
- [ ] Confirmar que o PDF continua sendo gerado corretamente.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/geracao-de-curriculo/job-0002-destaque-bold-no-pdf-curriculo/prd-job-0002.md`
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0002-destaque-bold-no-pdf-curriculo/techspec-job-0002.md`
- `infrastructure/pdf/gerador_pdf_reportlab.py`

# Tarefa 8.0: Validação visual contra o modelo, suíte completa e lint-imports

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Fechar o JOB: comparar o PDF gerado com o modelo de referência, ajustar espaçamentos finos, rodar todos os testes e os contratos de arquitetura.

<requirements>
- Gerar um PDF com o mesmo conteúdo de `modelo-referencia-curriculo-en.pdf` (idioma `en`) e outro em `pt`.
- Comparar lado a lado com o modelo (`pdftoppm -r 80`) e ajustar espaçamentos em `EstiloCurriculoPdf` quando houver diferença visível.
- Toda a suíte `pytest` deve passar.
- `lint-imports` deve passar (contratos do `setup.cfg`).
- Imagens da comparação anexadas ao PR.
- Atualizar a checklist em `resumo-tasks-job-0016.md`.
</requirements>

## Subtarefas

- [ ] 8.1 Criar script descartável (no scratchpad, fora do repositório) que gera o PDF com o conteúdo do modelo.
- [ ] 8.2 Gerar as imagens do modelo e do PDF novo e comparar.
- [ ] 8.3 Ajustar espaçamentos finos, se necessário, mantendo os testes verdes.
- [ ] 8.4 Rodar `pytest` e `lint-imports`.
- [ ] 8.5 Verificar a geração pela API (`POST` de adaptação de currículo) e pelo Streamlit, se o ambiente permitir.
- [ ] 8.6 Marcar as tarefas concluídas no resumo.

## Detalhes de Implementação

Consultar em `techspec-job-0016.md` a seção "Testes de Serviço" e a tabela de medidas.

## Critérios de Sucesso

- Comparação visual aprovada pelo candidato (critério de aceite do PRD).
- Suíte de testes e `lint-imports` verdes.
- Geração de PDF abaixo de 1 s para currículo de 2 páginas (sem contar IA).

## Testes da Tarefa

- [ ] `pytest` completo.
- [ ] `lint-imports`.
- [ ] Comparação visual en e pt.
- [ ] Medição de tempo de geração do PDF.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/geracao-de-curriculo/job-0016-layout-pdf-curriculo-modelo-referencia/modelo-referencia-curriculo-en.pdf`
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0016-layout-pdf-curriculo-modelo-referencia/resumo-tasks-job-0016.md`
- `src/jobsync/curriculo/adapters/pdf/estilo_curriculo_pdf.py`
- `setup.cfg`

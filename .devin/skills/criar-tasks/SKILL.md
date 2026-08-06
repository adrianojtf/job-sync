---
name: criar-tasks
description: Geração de tarefas a partir de um PRD e uma Tech Spec
triggers:
  - user
  - model
allowed-tools:
  - read
  - grep
  - glob
  - exec
  - edit
  - write
---

# Criação de Tasks

Este skill define o fluxo, regras e formato para geração de tarefas a partir de um PRD e uma Tech Spec.

## Objetivo

Criar uma lista de tarefas detalhada e orientada para entrega incremental, com critérios de sucesso e testes claros, sem implementar nada.

## Fluxo

1. Confirmar a existência do PRD e da Tech Spec em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/`.
2. Revisar os documentos e extrair requisitos, entregáveis e dependências.
3. Gerar uma lista high level de tarefas principais para aprovação antes de criar arquivos.
4. Após aprovação, criar o resumo de tarefas usando `/sdd/templates/resumo-tasks-template.md`.
5. Criar arquivos de tarefa individuais usando `/sdd/templates/task-template.md`.
6. Cada tarefa deve ser um entregável funcional e incluir testes de unidade quando aplicável.
7. Fornecer o caminho final dos arquivos e um resumo das decisões.

## Regras obrigatórias

- Antes de gerar qualquer arquivo, mostrar a lista das tasks high level para aprovação.
- Não implementar nada; foco na definição de tarefas.
- Cada tarefa deve ser um entregável funcional e incremental.
- Definir um conjunto de testes para cada tarefa, sempre que aplicável.
- Limitar a lista a no máximo 10 tarefas principais.
- Usar o template `/sdd/templates/resumo-tasks-template.md` para o resumo de tarefas.
- Usar o template `/sdd/templates/task-template.md` para tarefas individuais.
- Nomear tarefas principais como X.0 e subtarefas como X.Y.
- Indicar dependências e a complexidade (low/medium/high) de cada tarefa.

## Pré-requisitos

- PRD em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/prd-[codigo-jira].md`
- Tech Spec em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/techspec-[codigo-jira].md`
- Template de resumo de tarefas em `/sdd/templates/resumo-tasks-template.md`
- Template de tarefa individual em `/sdd/templates/task-template.md`

## Estrutura esperada

- Resumo de tarefas com entregáveis principais e dependências
- Arquivos de tarefa individuais com subtarefas e critérios de sucesso
- Testes de unidade ou validação para cada tarefa aplicável

## Localização de arquivos

- Template resumo: `/sdd/templates/resumo-tasks-template.md`
- Template tarefa: `/sdd/templates/task-template.md`
- Resultado resumo: `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/resumo-tasks-[codigo-jira].md`
- Tarefas individuais: `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/task-[codigo-jira]-[numero-da-tarefa].md`

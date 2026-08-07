---
name: preparar-sdd-e-branch
description: Executa o fluxo completo de planejamento de uma feature (PRD, Tech Spec, tasks) e prepara o git
argument-hint: "[caminho-input-prd]"
triggers:
  - user
  - model
allowed-tools:
  - read
  - write
  - edit
  - exec
  - grep
  - glob
  - skill
  - ask_user_question
  - find_file_by_name
---

# Preparar SDD e branch

Este skill orquestra a criação dos artefatos de planejamento de uma feature (PRD, Tech Spec e tasks) e a preparação do git para o desenvolvimento.

## Entradas

O usuário pode informar:

1. O caminho de um arquivo de input preenchido com base em `/sdd/templates/input-prd-template.md`, ou
2. Os dados diretamente na conversa.

Campos obrigatórios:

- `código-jira`
- `módulo`
- `subsistema`
- `resumo da funcionalidade` (em kebab-case; se omitido, gerar a partir do contexto)
- `requisitos` (descrição da feature)

## Fluxo

1. Valide os campos obrigatórios. Se faltar algum, pergunte ao usuário.
2. Verifique o estado do git (`git status --short`).
   - Se houver mudanças não commitadas, avise o usuário e pergunte se deseja stash, descartar, commitar manualmente ou parar.
   - Prossiga com o git somente quando a árvore estiver limpa ou o usuário confirmar.
3. Invocar o skill `criar-prd` com as informações coletadas.
4. Confirmar que o PRD foi salvo em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo]/prd-[codigo-jira].md`.
5. Invocar o skill `criar-techspec`.
6. Confirmar que a Tech Spec foi salva em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo]/techspec-[codigo-jira].md`.
7. Invocar o skill `criar-tasks`.
8. Confirmar que o resumo de tasks e as tasks individuais foram salvas em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo]/`.
9. Monte o nome sugerido da branch: `feature-[código-jira]-[resumo]`.
   - Pergunte ao usuário se ele deseja usar esse nome ou outro.
10. Execute os comandos git:
    - `git checkout main`
    - `git pull origin main`
    - `git checkout -b <nome-da-branch>`
11. Informe o resumo do que foi gerado (caminhos dos arquivos e nome da branch). Liste eventuais questões em aberto.

## Regras

- Não gerar documentos antes de validar os placeholders obrigatórios.
- Não perder alterações locais: sempre verifique `git status` antes de trocar de branch.
- Só crie a nova branch se a árvore de trabalho estiver limpa ou o usuário confirmar o procedimento.
- Não fazer commit ou push automaticamente.

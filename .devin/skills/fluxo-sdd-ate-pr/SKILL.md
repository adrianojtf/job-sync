---
name: fluxo-sdd-ate-pr
description: Orquestra o fluxo completo de feature no job-sync: planejamento SDD, branch, execução de tasks, commits, push e criação de PR para aprovação
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
  - find_file_by_name
  - skill
  - ask_user_question
  - mcp_list_tools
  - mcp_call_tool
---

# Fluxo SDD até PR

Este skill orquestra todo o ciclo de uma feature no job-sync: criação dos artefatos de planejamento (PRD, Tech Spec e tasks), preparação da branch, execução das tasks, commit, push e criação do Pull Request para o usuário aprovar.

## Entradas

O usuário pode informar:

1. O caminho de um arquivo de input preenchido com base em `/sdd/templates/input-prd-template.md`, ou
2. Os dados diretamente na conversa.

Campos obrigatórios (caso não venham por arquivo):

- `código-jira`
- `módulo`
- `subsistema`
- `resumo da funcionalidade` (em kebab-case; se omitido, gerar a partir do contexto)
- `requisitos` (descrição da feature)

## Fluxo

### Fase 1 — Preparar SDD e branch

1. Valide os campos obrigatórios. Se faltar algum, pergunte ao usuário.
2. Verifique o estado do git (`git status --short`).
   - Se houver mudanças não commitadas, avise o usuário e pergunte se deseja stash, descartar, commitar manualmente ou parar.
   - Prossiga somente quando a árvore estiver limpa ou o usuário confirmar.
3. Invocar o skill `preparar-sdd-e-branch` com as informações coletadas.
4. Capture o nome da branch criada e os caminhos dos artefatos gerados:
   - `/sdd/specs/[modulo]/[subsistema]/[código-jira]-[resumo]/prd-[código-jira].md`
   - `/sdd/specs/[modulo]/[subsistema]/[código-jira]-[resumo]/techspec-[código-jira].md`
   - `/sdd/specs/[modulo]/[subsistema]/[código-jira]-[resumo]/resumo-tasks-[código-jira].md`

### Fase 2 — Executar tasks e commitar

1. Pergunte ao usuário se deseja prosseguir para a execução das tasks.
2. Determine o caminho do resumo de tasks: `/sdd/specs/[modulo]/[subsistema]/[código-jira]-[resumo]/resumo-tasks-[código-jira].md`.
3. Invocar o skill `executar-tasks-e-commitar` com esse caminho.
4. Confirme que as tasks foram executadas e os commits feitos.

### Fase 3 — Push

1. Verifique se há commits na branch local ainda não presentes no remote (`git log origin/<branch>..<branch> --oneline`).
2. Pergunte ao usuário se deseja fazer push e criar o PR.
3. Só após confirmação, execute `git push -u origin <branch>`.

### Fase 4 — Criar o PR

1. Invocar o skill `criar-pr` (com o nome da branch atual) ou, se não estiver disponível, monte o PR manualmente:
   - Identifique o repositório remoto com `git remote -v` e extraia `owner` e `repo`.
   - Título: `feat(<módulo>/<subsistema>): [<código-jira>] <resumo>` (ex: `feat(plataforma-base/perfil-estruturado): [SIRT-203] curriculo-mestre`).
   - Corpo: resumo da feature, link para o `prd-[código-jira].md`, principais decisões técnicas, pontos em aberto e referência ao `techspec-[código-jira].md`.
2. Liste as ferramentas do `github-mcp-server` via `mcp_list_tools` e localize `create_pull_request`.
3. Crie o PR via `mcp_call_tool` com:
   - `owner` e `repo` extraídos do remote
   - `title`
   - `body`
   - `head`: nome da branch
   - `base`: `main`
   - `draft`: `true`
4. Se o GitHub MCP falhar e o `gh` CLI estiver instalado, tente `gh pr create --draft --title "..." --body "..." --base main`.
5. Informe a URL do PR e instrua que o PR foi deixado em draft/para revisão para o usuário aprovar quando desejar.

## Regras

- Não execute push nem criação de PR sem confirmação explícita do usuário.
- Não faça merge do PR. Deixe em rascunho para aprovação do usuário.
- Não altere a configuração do git (`user.name`, `user.email` etc.).
- Respeite o padrão de specs do job-sync: `/sdd/specs/[modulo]/[subsistema]/[código-jira]-[resumo]/`.
- Respeite o estilo de commits do job-sync (`JOB-[código-jira] task X: ...`).
- Se qualquer fase falhar, pare o fluxo, informe o usuário com o erro e sugira a próxima ação.

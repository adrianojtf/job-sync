---
name: criar-pr
description: Faz push da branch atual e cria um Pull Request draft no job-sync para aprovação do usuário
argument-hint: "[nome-da-branch]"
triggers:
  - user
  - model
allowed-tools:
  - read
  - exec
  - grep
  - find_file_by_name
  - ask_user_question
  - mcp_list_tools
  - mcp_call_tool
---

# Criar PR

Este skill faz o push da branch local e cria um Pull Request draft no repositório do job-sync, para que o usuário revise e aprove.

## Entradas

O usuário pode informar opcionalmente:

- `nome-da-branch`: o nome da branch a ser enviada. Se omitido, usa a branch atual (`git branch --show-current`).

## Fluxo

1. Determine a branch:
   - Se o usuário informou um nome, use-o.
   - Caso contrário, execute `git branch --show-current`.
2. Verifique se existem commits pendentes de push:
   - Tente `git log origin/<branch>..<branch> --oneline`.
   - Se o remoto ainda não existir (branch nova), considere todos os commits locais como pendentes.
3. Pergunte ao usuário se deseja fazer push e criar o PR.
4. Somente após confirmação, execute:
   - `git push -u origin <branch>`
5. Identifique o repositório remoto com `git remote -v` e extraia `owner` e `repo`.
6. Tente inferir `código-jira`, `módulo`, `subsistema` e `resumo` a partir do nome da branch (`feature-[código-jira]-[resumo]`) ou procure por `/sdd/specs/**/prd-[código-jira].md`.
7. Monte o conteúdo do PR:
   - Título: `feat(<módulo>/<subsistema>): [<código-jira>] <resumo>` se for possível inferir.
   - Caso contrário, use `feat: <branch>` ou `feat: implementação da branch <branch>`.
   - Corpo: resumo breve, links para `prd-[código-jira].md` e `techspec-[código-jira].md` (se existirem), principais decisões e pontos em aberto.
8. Liste as ferramentas do `github-mcp-server` via `mcp_list_tools` e localize `create_pull_request`.
9. Crie o PR via `mcp_call_tool` com:
   - `owner` e `repo` extraídos do remote
   - `title`
   - `body`
   - `head`: nome da branch
   - `base`: `main`
   - `draft`: `true`
10. Se o GitHub MCP falhar e o `gh` CLI estiver instalado, tente como fallback:
    - `gh pr create --draft --title "..." --body "..." --base main`
11. Informe a URL do PR e confirme que ele foi criado como draft para aprovação.

## Regras

- Não faça push sem confirmação explícita do usuário.
- Não faça merge do PR.
- Crie o PR como draft por padrão, para que o usuário possa aprovar quando desejar.
- Não altere a configuração do git (`user.name`, `user.email` etc.).
- Se não houver commits para enviar, aborte o fluxo e avise o usuário.

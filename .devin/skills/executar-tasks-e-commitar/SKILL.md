---
name: executar-tasks-e-commitar
description: Executa as tasks geradas pelo SDD uma a uma e faz commit a cada tarefa concluída
argument-hint: "[caminho-resumo-tasks]"
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
---

# Executar tasks e commitar

Este skill itera pelas tasks do resumo de tarefas, executa cada uma com o skill `executar-task` e faz um commit individual ao final de cada task.

## Entrada

O usuário pode informar o caminho do resumo de tasks, por exemplo:

```
/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo]/resumo-tasks-[codigo-jira].md
```

Se não for informado, procure no padrão `sdd/specs/**/resumo-tasks-*.md` e peça confirmação do arquivo correto.

## Fluxo

1. Leia o resumo de tasks e identifique as tasks marcadas como pendentes.
2. Pergunte ao usuário se deseja executar todas as pendentes e comitar uma a uma. Só prossiga após confirmação.
3. Para cada task pendente:
   1. Invocar o skill `executar-task`.
   2. Aguarde a conclusão. O skill `executar-task` já deverá ter marcado a task como completa no resumo.
   3. Verifique `git status --short`.
   4. Se houver alterações, faça o commit com uma mensagem descritiva da task:
      - Identifique os arquivos alterados/criados.
      - Execute `git add <arquivos>`.
      - Execute `git commit -m "<mensagem>"`.
      - A mensagem deve seguir o formato: `JOB-[codigo-jira] task X: <título breve>`.
   5. Se não houver alterações, pule o commit e avise.
4. Ao final, informe quais tasks foram executadas e os commits feitos.

## Regras

- Não execute nada sem confirmar com o usuário na primeira interação.
- Não faça `git push`.
- Não altere a configuração do git (user.name, user.email etc.).
- Se uma task falhar nos testes, o skill `executar-task` solicitará ajustes. Não prossiga para a próxima task enquanto a atual não estiver concluída e os testes passando.
- Só faça commit se existirem mudanças.
- A mensagem de commit deve focar no "porquê", não apenas no "o quê".

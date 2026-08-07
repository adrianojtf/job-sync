# Executar tasks e commitar

Este documento descreve como executar o agente que implementa as tasks geradas no SDD e faz um commit individual a cada tarefa concluída.

## O que o agente faz

O agente, representado pela skill `executar-tasks-e-commitar`, executa o seguinte fluxo:

1. Lê o resumo de tasks (`resumo-tasks-[codigo-jira].md`).
2. Identifica as tasks pendentes.
3. Para cada task:
   - Executa a implementação com a skill `executar-task`.
   - Garante que os testes relacionados estejam passando.
   - Faz o commit das alterações com uma mensagem descritiva.

## Pré-requisitos

- O PRD, Tech Spec e resumo de tasks já devem existir (gerados pelo agente de SDD).
- O ambiente git deve estar configurado com `user.name` e `user.email`.
- O agente não fará `push`; os commits ficarão locais até que você decida enviá-los.

## Como informar o resumo de tasks

O agente precisa do caminho do resumo de tasks. O padrão é:

```
sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo]/resumo-tasks-[codigo-jira].md
```

Exemplo:

```
sdd/specs/curriculo/adaptacao/job-0042-adaptar-curriculo-para-vaga/resumo-tasks-job-0042.md
```

## Como executar

No chat, digite:

```
/executar-tasks-e-commitar <caminho-do-resumo-tasks>
```

Exemplo:

```
/executar-tasks-e-commitar sdd/specs/curriculo/adaptacao/job-0042-adaptar-curriculo-para-vaga/resumo-tasks-job-0042.md
```

Se preferir que eu inicie o agente, basta pedir:

> Execute as tasks do resumo `sdd/specs/.../resumo-tasks-job-0042.md` e commita a cada uma.

## Fluxo de execução

1. O agente pede confirmação antes de começar.
2. Executa a próxima task pendente.
3. Quando a task concluir, verifica as mudanças no git.
4. Se houver alterações, faz o commit com a mensagem:

   ```
   JOB-[codigo-jira] task [número]: [título breve]
   ```

5. Continua para a próxima task até que todas estejam concluídas.
6. Informa o resumo de tudo que foi feito.

## Observações

- O agente não faz `git push`.
- Se uma task falhar nos testes, o agente não avança para a próxima.
- Se não houver alterações após uma task, o commit é pulado.
- O agente não altera a configuração do git.

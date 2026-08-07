# Executar agente de SDD

Este documento descreve como executar o agente que cria os artefatos de planejamento (PRD, Tech Spec e tasks) e prepara o ambiente git para uma nova feature.

## O que o agente faz

O agente, representado pela skill `preparar-sdd-e-branch`, executa o seguinte fluxo:

1. Valida as informações da feature.
2. Cria o PRD com a skill `criar-prd`.
3. Cria a Tech Spec com a skill `criar-techspec`.
4. Cria o resumo de tasks e as tasks individuais com a skill `criar-tasks`.
5. Prepara o git: `checkout main`, `pull origin main` e `checkout -b <branch>`.

## Pré-requisitos

A árvore de trabalho deve estar limpa antes da parte do git. Se houver alterações não commitadas, o agente pedirá instruções (stash, descartar, commitar manualmente ou parar).

## Como informar os dados da feature

### Opção 1: arquivo de input

Copie o template de input e preencha os campos obrigatórios:

```bash
cp sdd/templates/input-prd-template.md sdd/inputs/meu-input.md
```

Edite `sdd/inputs/meu-input.md` com:

- **Código Jira**: ex. `JOB-0042`
- **Módulo**: ex. `curriculo`, `candidatura`, `vaga`
- **Subsistema**: ex. `adaptacao`, `captura`, `match`
- **Resumo da funcionalidade**: em kebab-case, ex. `adaptar-curriculo-para-vaga`
- **Requisitos**: descrição da feature, user stories ou listas de comportamento esperado

### Opção 2: informar na conversa

Se não quiser usar um arquivo, informe os mesmos campos diretamente quando o agente perguntar.

## Como executar

No chat, digite:

```
/preparar-sdd-e-branch <caminho-do-input>
```

Exemplo:

```
/preparar-sdd-e-branch sdd/inputs/job-0042-adaptar-curriculo-para-vaga.md
```

Se preferir que eu inicie o agente, basta pedir:

> Execute o agente de SDD para o input `sdd/inputs/meu-input.md`.

## Resultado esperado

O agente criará os arquivos no diretório:

```
sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo]/
├── prd-[codigo-jira].md
├── techspec-[codigo-jira].md
├── resumo-tasks-[codigo-jira].md
└── task-[codigo-jira]-<n>.md
```

E uma nova branch com o nome sugerido `feature-[codigo-jira]-[resumo]`, a menos que outro nome seja informado.

## Observações

- O agente não faz commit ou push automaticamente.
- A parte do git só será executada se a árvore estiver limpa ou se você confirmar explicitamente.
- O resumo da funcionalidade pode ser omitido; nesse caso, o agente gera um resumo em kebab-case com base nos requisitos.

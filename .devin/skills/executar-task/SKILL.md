---
name: executar-task
description: Implementar tarefas do resumo de tasks com base no PRD, Tech Spec e regras do projeto
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

# Executar Task

Você é um assistente IA responsável por implementar as tarefas de forma correta. Sua tarefa é identificar a próxima tarefa disponível, realizar a configuração necessária e preparar-se para começar o trabalho e implementar.

## Entradas

- PRD: `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/prd-[codigo-jira].md`
- Tech Spec: `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/techspec-[codigo-jira].md`
- Tasks: `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/resumo-tasks-[codigo-jira].md`
- Regras do Projeto: `/.windsurf/rules` e `AGENTS.md`

## Etapas

### 1. Configuração Pré-Tarefa

- Ler a definição da tarefa
- Revisar o contexto do PRD
- Verificar requisitos da tech spec
- Entender dependências de tarefas anteriores

### 2. Análise da Tarefa

Analise considerando:

- Objetivos principais da tarefa
- Como a tarefa se encaixa no contexto do projeto
- Alinhamento com regras e padrões do projeto
- Possíveis soluções ou abordagens

### 3. Resumo da Tarefa

```
ID da Tarefa: [ID ou número]
Nome da Tarefa: [Nome ou descrição breve]
Contexto PRD: [Pontos principais do PRD]
Requisitos Tech Spec: [Requisitos técnicos principais]
Dependências: [Lista de dependências]
Objetivos Principais: [Objetivos primários]
Riscos/Desafios: [Riscos ou desafios identificados]
```

### 4. Plano de Abordagem

```
1. [Primeiro passo]
2. [Segundo passo]
3. [Passos adicionais conforme necessário]
```

Não pule nenhum passo.

## Notas importantes

- Sempre verifique o PRD, tech spec e arquivo de tarefa.
- Implemente soluções adequadas **sem usar gambiarras**.
- Siga todos os padrões estabelecidos do projeto.
- Utilize o Context7 MCP para analisar a documentação da linguagem, frameworks e bibliotecas envolvidas na implementação.
- Priorize o uso do `intellij-code-analysis` MCP para explorar o código.
- **Não faça auto commit**. O controle de versionamento e criação de commits deve ser feito pelo usuário ou pela ferramenta de integração, nunca de forma automática por esta skill.

## Implementação

Após fornecer o resumo e abordagem, comece imediatamente a implementar a tarefa:
- Executar comandos necessários
- Fazer alterações de código
- Seguir padrões estabelecidos do projeto
- Garantir que todos os requisitos sejam atendidos
- Garantir que todos os testes envolvidos com o código que foi criado/alterado estão passando. Caso estejam falhando, analise o motivo e identifique as correções necessárias. Solicite confirmação para executar essas correções. Se autorizado, faça as correções e execute este item novamente (rodando os testes e garantindo que estão passando).

A tarefa não pode ser considerada completa enquanto todos os testes não estiverem passando.
Após completar a tarefa, **marque como completa em `resumo-tasks-[codigo-jira].md`**.

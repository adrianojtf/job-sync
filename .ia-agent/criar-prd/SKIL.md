# Skill: Criação de PRD

Este skill descreve o fluxo, regras e formato para criação de Product Requirement Documents (PRDs) no repositório.

## Objetivo

Gerar um PRD claro, acionável e padronizado a partir de requisitos iniciais informados pelo usuário, seguindo o template e o diretório definidos.

## Fluxo do skill

1. Solicitar ou verificar o arquivo de input inicial com os requisitos.
2. Fazer perguntas de clarificação numeradas antes de qualquer tentativa de gerar o PRD.
3. Criar um plano de desenvolvimento do PRD seção por seção.
4. Redigir o PRD usando o template `/sdd/templates/prd-template.md`.
5. Criar ou verificar o diretório final em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/`.
6. Salvar o PRD em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/prd-[codigo-jira].md`.
7. Informar o caminho do arquivo final, o resumo das decisões tomadas e as questões em aberto.

## Regras obrigatórias

- Não gerar o PRD antes de fazer perguntas de clarificação numeradas.
- Usar sempre o template `/sdd/templates/prd-template.md`.
- Validar a presença dos placeholders no input inicial: `[modulo]`, `[subsistema]`, `[codigo-jira]`, `[resumo-funcionalidade]`.
- Se faltar algum placeholder obrigatório, solicitar a informação ao usuário.
- Se não houver `[resumo-funcionalidade]`, gerar um resumo em kebab-case baseado no contexto.
- O nome do diretório e do arquivo final não devem conter letras maiúsculas.
- Focar no "quê" e no "porquê", não no "como".
- Incluir requisitos funcionais numerados no PRD.
- Manter o PRD em no máximo 2.000 palavras.

## Estrutura esperada do PRD

- Objetivo do negócio
- Problema a resolver
- Usuários e personas
- Funcionalidade principal
- Escopo e exclusões
- Requisitos funcionais numerados
- Requisitos não funcionais
- Critérios de aceitação
- Restrições e dependências
- Questões em aberto

## Localização de arquivos

- Template: `/sdd/templates/prd-template.md`
- Resultado: `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/prd-[codigo-jira].md`

## Notas

- Criar os diretórios necessários automaticamente quando o skill estiver produzindo o arquivo.
- Garantir que o output contenha o caminho final do arquivo e um resumo das decisões tomadas.
- Em caso de dúvidas sobre escopo ou requisitos, listar explicitamente as questões em aberto.

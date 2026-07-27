# Skill: Criação de Tech Spec

Este skill define o fluxo, regras e formato para geração de Tech Specs a partir de um PRD existente.

## Objetivo

Traduzir requisitos do PRD em uma especificação técnica clara, focada em arquitetura e pronta para implementação, usando o template padrão.

## Fluxo do skill

1. Confirmar a existência do PRD em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/prd-[codigo-jira].md`.
2. Revisar o PRD completo e extrair requisitos, restrições e métricas de sucesso.
3. Analisar o projeto e identificar classes, componentes, módulos e pontos de integração existentes.
4. Fazer perguntas de clarificação técnicas numeradas antes de gerar a Tech Spec.
5. Mapear conformidade com `/.windsurf/rules` e documentar quaisquer desvios.
6. Gerar a Tech Spec usando o template `/sdd/templates/techspec-template.md`.
7. Salvar o documento em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/techspec-[codigo-jira].md`.
8. Informar o caminho final, decisões tomadas e questões em aberto.

## Regras obrigatórias

- Não gerar a Tech Spec sem antes fazer perguntas de clarificação numeradas.
- Usar sempre o template `/sdd/templates/techspec-template.md`.
- Revisar e referenciar o PRD existente antes de redigir o documento.
- Priorizar bibliotecas, componentes e padrões existentes do projeto.
- Focar em COMO implementar, não em repetir requisitos funcionais do PRD.
- Limitar o documento a aproximadamente 2.000 palavras.
- Incluir análise de impacto, estratégia de testes e observabilidade.
- Documentar desvios das regras de `/.windsurf/rules` com justificativas.

## Pré-requisitos

- O PRD deve existir em `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/prd-[codigo-jira].md`.
- O template deve estar disponível em `/sdd/templates/techspec-template.md`.
- Revisar padrões do projeto em `/.windsurf/rules`.

## Estrutura esperada da Tech Spec

- Visão geral da solução
- Arquitetura proposta
- Design de componentes e interfaces
- Modelos de dados e contratos
- Endpoints, integração e fluxo de dados
- Considerações de testes e observabilidade
- Análise de impacto e riscos
- Dependências e restrições
- Questões em aberto

## Localização de arquivos

- Template: `/sdd/templates/techspec-template.md`
- Resultado: `/sdd/specs/[modulo]/[subsistema]/[codigo-jira]-[resumo-funcionalidade]/techspec-[codigo-jira].md`

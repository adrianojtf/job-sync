# Tarefa 6.0: Componente SugestaoIA

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar o componente compartilhado que pede, mostra e aplica ou descarta uma sugestão, sem saber em qual tela está.

<requirements>
- Props: `rotuloBloco`, `obterTextoAtual`, `sugerir`, `aplicar`.
- Botão "Sugestões de IA" desabilitado com campo vazio; carregamento e erro por bloco.
- Painel "Sugestão da IA" com texto atual e sugerido, Aplicar e Descartar com rótulos por bloco.
- `aria-live="polite"` na chegada; foco volta ao campo após decidir.
- Nova sugestão substitui a anterior; a sugestão nunca sobrescreve o campo sozinha.
- Complexidade: medium. Dependências: 5.0.
</requirements>

## Subtarefas

- [ ] 6.1 Testes do componente (Red).
- [ ] 6.2 Componente e CSS.

## Detalhes de Implementação

Ver "Componente compartilhado (frontend)" em `techspec-job-0034.md`.

## Critérios de Sucesso

- Todos os comportamentos do PRD RF11–RF18 cobertos por testes.

## Testes da Tarefa

- [ ] Testes de unidade (Vitest) de `SugestaoIA`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/SugestaoIA.tsx`
- `frontend/src/shared/formulario-curriculo/SugestaoIA.module.css`

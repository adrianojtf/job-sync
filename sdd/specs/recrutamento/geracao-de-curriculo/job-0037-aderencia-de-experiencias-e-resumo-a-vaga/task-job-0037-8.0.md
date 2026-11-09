# Tarefa 8.0: Tela de revisão: ajustes de tecnologia, aviso e cargo-alvo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

A revisão mostra as trocas feitas pela IA, atualiza o aviso de conferência e envia o cargo-alvo nas sugestões.

<requirements>
- `AjusteTecnologiaLista`: título "Ajustes de tecnologia", lista "original → alvo em cargo — empresa"; não aparece sem ajustes (RF14, RF16).
- Aviso do topo inclui trocas e responsabilidades implícitas (RF15).
- `AjustarVagaPage` monta `contextoVaga` com `cargo_alvo`.
- Complexidade: medium. Dependências: 6.0.
</requirements>

## Subtarefas

- [x] 8.1 Testes da lista, do aviso e do contexto (Red).
- [x] 8.2 `AjusteTecnologiaLista`.
- [x] 8.3 `RevisaoCurriculoAdaptado` e `AjustarVagaPage`.

## Detalhes de Implementação

Ver "Experiência do Usuário" no PRD e componentes de frontend em `techspec-job-0037.md`.

## Critérios de Sucesso

- Lista com marcação semântica e título; ausente sem ajustes.
- Todas as sugestões da revisão enviam o `cargo_alvo`.

## Testes da Tarefa

- [x] Vitest de `AjusteTecnologiaLista`, `RevisaoCurriculoAdaptado` e `AjustarVagaPage`; lint, `tsc` e build.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/ajustar-vaga/{AjusteTecnologiaLista.tsx,RevisaoCurriculoAdaptado.tsx,AjustarVagaPage.tsx}`

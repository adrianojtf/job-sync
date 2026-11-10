# Tarefa 5.0: Lógica do board no frontend e atualização otimista

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Funções puras que calculam o destino do arrasto e o novo quadro, mais o hook de mover com atualização otimista. A UI da tarefa 6.0 usa tudo isso.

<requirements>
- `movimento.ts` com `calcularDestino(quadro, ativoId, sobreId)` e `aplicarMovimento(quadro, ativoId, destino)`; `sobreId` pode ser um cartão ou `coluna:STATUS`; soltar na mesma posição devolve `null`.
- `formatarTempoRelativo(data)` em `shared/formatacao.ts` ("hoje", "há 1 dia", "há 3 dias", e assim por diante).
- `useMoverCandidatura` com `onMutate` (cancela consultas e grava o novo quadro no cache), `onError` (restaura o cache) e `onSettled` (invalida), com `mutationKey` para serializar movimentos.
- Hook `use-mover-com-aviso.ts` que junta a mutation e o toast de sucesso ("Candidatura movida para X.") e de erro, usado pelo arrasto e pelo modal.
- `COR_STATUS` em `status.ts` com o tom de cada coluna.
</requirements>

## Subtarefas

- [x] 5.1 Escrever os testes de `movimento.ts` e de `formatarTempoRelativo` (red).
- [x] 5.2 Implementar as funções puras.
- [x] 5.3 Escrever os testes do hook (sucesso, erro com restauração, dois movimentos seguidos).
- [x] 5.4 Implementar `useMoverCandidatura` otimista e `use-mover-com-aviso.ts`.
- [x] 5.5 Adicionar `COR_STATUS`.

## Detalhes de Implementação

Techspec: "Interfaces Principais" (`movimento.ts`), "Fluxo de dados" e "Decisões Principais" (atualização otimista). PRD: RF3, RF4, RF6.

## Critérios de Sucesso

- O cache reflete o movimento antes da resposta da API e volta ao estado anterior em caso de erro.
- Funções puras sem dependência de React, com cobertura dos casos de borda.

## Testes da Tarefa

- [x] `movimento.test.ts`: entre colunas, mesma coluna, coluna vazia, soltar sobre a própria posição.
- [x] `formatacao.test.ts`: tempo relativo.
- [x] Hook: sucesso, erro com restauração do cache e toast, dois movimentos seguidos.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- frontend/src/features/candidaturas/movimento.ts (novo)
- `frontend/src/features/candidaturas/use-candidaturas.ts`
- frontend/src/features/candidaturas/use-mover-com-aviso.ts (novo)
- `frontend/src/features/candidaturas/status.ts`
- `frontend/src/shared/formatacao.ts`
- `frontend/src/shared/formatacao.test.ts`

# Tarefa 6.0: Componentes do board e interações

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Monta o board com `DndContext`: coluna, cartão ordenável, overlay de arrasto, anúncios em português, título que abre o detalhe e o campo "Mover para" no modal. Remove o `select` e o botão "Detalhes" dos cartões.

<requirements>
- `ColunaKanban.tsx` (cabeçalho, contagem, `useDroppable` e `SortableContext`) e `CartaoCandidatura.tsx` (`useSortable`, título em botão), conforme a decisão da tarefa 4.0.
- `CandidaturasPage.tsx` com sensores, `closestCorners`, `DragOverlay` e `autoScroll`; Esc ou soltar fora cancela o movimento.
- `anuncios.ts` com os textos de acessibilidade em pt-BR.
- A página guarda só o `id` da candidatura em detalhe e a lê do cache.
- `DetalheCandidaturaModal` ganha o `select` "Mover para" (quatro status), que chama `mover` com `posicao: 0` pelo hook `use-mover-com-aviso`.
- Remover o `select` e o botão "Detalhes" do cartão. Manter os estados de carregando, erro e vazio.
</requirements>

## Subtarefas

- [ ] 6.1 Reescrever os testes da página (sem `select` e sem "Detalhes"; título abre o detalhe) (red).
- [ ] 6.2 Criar `CartaoCandidatura` e `ColunaKanban`.
- [ ] 6.3 Montar o `DndContext`, o overlay, o cancelamento e os anúncios.
- [ ] 6.4 Ligar o título ao detalhe e guardar só o `id`.
- [ ] 6.5 Adicionar "Mover para" ao modal e testar o sucesso e o erro.
- [ ] 6.6 Remover o código antigo do cartão.

## Detalhes de Implementação

Techspec: "Visão Geral dos Componentes" (frontend), "Interfaces Principais" (sensores e modal). PRD: RF1, RF12–RF18b.

## Critérios de Sucesso

- Arrastar entre colunas e dentro da coluna funciona e persiste.
- O detalhe abre só por clique ou Enter no título, nunca após um arrasto.
- "Mover para" no modal move para o topo da coluna e atualiza o status exibido no modal e no board.
- Não resta `select` nem botão "Detalhes" nos cartões.

## Testes da Tarefa

- [ ] Teste da página: título abre o detalhe; não há `select` nem "Detalhes"; movimento por teclado (Espaço, seta, Espaço) envia `novo_status` e `posicao` corretos; erro da API restaura o cartão e mostra o toast; anúncios em pt-BR.
- [ ] Teste do modal: "Mover para" move, atualiza o status exibido e restaura o valor em erro.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/candidaturas/CandidaturasPage.tsx`
- frontend/src/features/candidaturas/ColunaKanban.tsx (novo)
- frontend/src/features/candidaturas/CartaoCandidatura.tsx (novo)
- frontend/src/features/candidaturas/anuncios.ts (novo)
- `frontend/src/features/candidaturas/DetalheCandidaturaModal.tsx`
- `frontend/src/features/candidaturas/CandidaturasPage.test.tsx`

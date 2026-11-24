# Tarefa 4.0: ListaItensCurriculo em modo cartão com reordenação, limite e ordenar por período

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

`ListaItensCurriculo` ganha o modo cartão recolhível e reordenável (mouse, toque, teclado e botões), com anúncios em português, limite de itens, ordenação por período e desfazer.

<requirements>
- Novas props opcionais: `modo`, `resumoDoItem`, `reordenavel`, `limite`, `ordenarPor`, `chaveDoItem`, `historico`; sem elas o componente se comporta como hoje (revisão do adaptado).
- `CartaoDaLista`: alça (`useSortable`), inicial, título, subtítulo, meta, chips, botão de abrir (`aria-expanded`) e botões "Mover para cima/baixo".
- DndContext com `MouseSensor` (distância 5), `TouchSensor` (atraso) e `KeyboardSensor`; `onDragEnd` chama `registrar()` e `move(de, para)`; cartões se recolhem durante o arrasto.
- `anuncios-de-lista.ts`: anúncios em português (pegar, mover, soltar, cancelar) com nome e posição.
- "Expandir/Recolher todas", "Ordenar por período" e "Adicionar" (desabilitado no limite, com explicação); item novo entra no topo, abre e recebe o foco; toast "Ordem alterada" com "Desfazer".
- Foco devolvido ao item após mover ou desfazer.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 4.1 Escrever os testes do componente nos três cenários (mock do `DndContext`, botões, limite, ordenar, desfazer) (red).
- [ ] 4.2 Implementar `CartaoDaLista` e os anúncios (green).
- [ ] 4.3 Implementar a reordenação, o limite e a ordenação em `ListaItensCurriculo` (green).
- [ ] 4.4 Refatorar e rodar `npm test`.

## Detalhes de Implementação

Techspec: "Interfaces Principais" e "Fluxo de dados". Referência: protótipo `sdd/prototipos/perfil_experiencias_prototipo.html` e o mock de `CandidaturasPage.test.tsx`. PRD: RF 1 a 7, 13 a 20 e 25 a 27.

Complexidade: high. Dependências: 2.0, 3.0.

## Critérios de Sucesso

- Qualquer item muda de posição por mouse, teclado e botões, e a mudança é desfeita pelo toast.
- A revisão do adaptado segue funcionando sem as props novas.

## Testes da Tarefa

- [ ] Vitest de `ListaItensCurriculo` e `CartaoDaLista`.
- [ ] Vitest dos anúncios.
- [ ] Regressão: `npm test`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/ListaItensCurriculo.tsx`
- `frontend/src/shared/formulario-curriculo/CartaoDaLista.tsx (novo)`
- `frontend/src/shared/formulario-curriculo/anuncios-de-lista.ts (novo)`
- `frontend/src/shared/formulario-curriculo/ListaItensCurriculo.test.tsx`
- `frontend/src/shared/formulario-curriculo/FormularioCurriculo.module.css`
- `frontend/src/features/candidaturas/CandidaturasPage.test.tsx (referência de mock)`

# Tarefa 8.0: Frontend: salvar ao confirmar, "Editar currículo" e modo edição

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Na tela "Ajustar para uma vaga", a confirmação da revisão passa a salvar o currículo adaptado. A tela do PDF ganha "Editar currículo", que reabre a revisão em modo edição, e a confirmação da candidatura envia o `curriculo_adaptado_id`.

<requirements>
- Confirmar a revisão chama `POST /curriculos-adaptados` e guarda o `id` junto do PDF.
- `CurriculoGerado` tem a ação "Editar currículo", que reabre `RevisaoCurriculoAdaptado` com o conteúdo salvo.
- `RevisaoCurriculoAdaptado` aceita o modo edição: o botão salva (`PUT`) em vez de gerar, e o PDF novo substitui o da tela.
- `contextoVaga` da edição vem do currículo salvo (descrição, idioma, análise e cargo), para as Sugestões de IA.
- `confirmarCandidatura` envia `curriculo_adaptado_id`.
- Cliente da API, tipos e hooks novos em `features/curriculos-adaptados/use-curriculos-adaptados.ts`.
- Estados de carregando e erro tratados como no restante da tela.
</requirements>

## Subtarefas

- [ ] 8.1 Testes de `AjustarVagaPage` (red): confirmar salva e mostra "Editar currículo"; editar atualiza o PDF; a candidatura envia o id.
- [ ] 8.2 Testes de `RevisaoCurriculoAdaptado` em modo edição (red).
- [ ] 8.3 Implementar o cliente da API e os hooks (green).
- [ ] 8.4 Alterar `AjustarVagaPage.tsx` e `use-ajustar-vaga.ts` (green).
- [ ] 8.5 Adicionar o modo edição a `RevisaoCurriculoAdaptado.tsx` (green).
- [ ] 8.6 Rodar lint e tipos do frontend.

## Detalhes de Implementação

Techspec: "Componentes" (frontend) e "Fluxo". PRD: RF 8, 9, 10 e 12.

## Critérios de Sucesso

- Depois de gerar o PDF, "Editar currículo" reabre a revisão com o mesmo conteúdo, e salvar atualiza o PDF.
- As Sugestões de IA na edição usam a vaga original.

## Testes da Tarefa

- [ ] Testes de unidade (Vitest e Testing Library).
- [ ] Regressão: `frontend/src/features/ajustar-vaga/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/ajustar-vaga/AjustarVagaPage.tsx`
- `frontend/src/features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx`
- `frontend/src/features/ajustar-vaga/use-ajustar-vaga.ts`
- `frontend/src/features/curriculos-adaptados/` (novo)
- `frontend/src/api/`

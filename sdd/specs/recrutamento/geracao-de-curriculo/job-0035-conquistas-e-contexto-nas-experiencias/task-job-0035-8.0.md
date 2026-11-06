# Tarefa 8.0: Tela de revisão

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Campos novos na revisão, aviso de números estimados e sugestão por experiência.

<requirements>
- Campos "Conquistas" (uma por linha) e "Contexto" no lugar da descrição.
- Aviso de números estimados, só com experiências estruturadas.
- `SugestaoExperienciaAdaptada`: aplica conquistas e contexto de uma vez.
- "Avaliar" usa o texto composto.
- Complexidade: high. Dependências: 7.0.
</requirements>

## Subtarefas

- [ ] 8.1 Testes (Red).
- [ ] 8.2 Campos e aviso.
- [ ] 8.3 Sugestão e avaliação.

## Detalhes de Implementação

Ver PRD RF7 a RF12.

## Critérios de Sucesso

- Todas as sugestões e edições da revisão cobertas por testes.

## Testes da Tarefa

- [ ] Testes de `RevisaoCurriculoAdaptado` e de `AjustarVagaPage`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/ajustar-vaga/`

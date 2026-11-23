# Tarefa 6.0: Aviso das lacunas na revisão

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Mostra, na revisão, as tecnologias da vaga que o perfil não sustenta, com a orientação de adicionar a tag.

Complexidade: low.

<requirements>
- Com lacunas, aparece "Tecnologias da vaga que seu perfil não mostra: ..." com a orientação de adicionar a tag.
- Sem lacunas, nada aparece.
- O aviso usa o componente `Aviso` e é legível por leitor de tela.
</requirements>

## Subtarefas

- [x] 6.1 Testes do componente e da revisão (red).
- [x] 6.2 Implementar o componente `LacunasTecnologiaAviso` e integrar na revisão (green).
- [x] 6.3 Rodar lint e tipos do frontend.

## Detalhes de Implementação

Techspec: "Design de Implementação" e "Abordagem de Testes". PRD: requisitos funcionais correspondentes.

## Critérios de Sucesso

- Os requisitos acima passam nos testes da tarefa.
- Nenhuma regressão nas JOB-0037, JOB-0040 e JOB-0041.

## Testes da Tarefa

- [x] Testes de unidade (Vitest e Testing Library).
- [x] Regressão: `frontend/src/features/ajustar-vaga/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx`
- `frontend/src/features/ajustar-vaga/AjusteTecnologiaLista.tsx` (modelo)

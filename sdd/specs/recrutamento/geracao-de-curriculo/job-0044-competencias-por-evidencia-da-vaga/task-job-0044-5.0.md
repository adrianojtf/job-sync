# Tarefa 5.0: Título "Competências" e "Skills": catálogo, PDF, tela e testes existentes

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Troca o nome da seção: "Competências" (pt) e "Skills" (en), no PDF e na tela.

Complexidade: low.

<requirements>
- O catálogo devolve "Competências" em português e "Skills" em inglês.
- O PDF usa esses títulos (o do rascunho continua ignorado, como antes).
- A tela da revisão e o padrão de `titulo_competencias` dizem "Competências".
- Testes e E2E que citam "Tecnologias" ou "Technical Skills" como título são atualizados.
</requirements>

## Subtarefas

- [x] 5.1 Testes do catálogo e do PDF (red).
- [x] 5.2 Alterar o catálogo, `TITULO_COMPETENCIAS_PADRAO` e o frontend (green).
- [x] 5.3 Atualizar os testes e o E2E existentes.

## Detalhes de Implementação

Techspec: "Design de Implementação" e "Abordagem de Testes". PRD: requisitos funcionais correspondentes.

## Critérios de Sucesso

- Os requisitos acima passam nos testes da tarefa.
- Nenhuma regressão nas JOB-0037, JOB-0040 e JOB-0041.

## Testes da Tarefa

- [x] Testes de unidade do catálogo e do PDF.
- [x] Regressão: backend e frontend.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/shared_kernel/domain/catalogo_localizacao.py`
- `src/jobsync/curriculo/domain/rascunho_curriculo_adaptado.py`
- `frontend/src/features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx`
- `frontend/src/features/ajustar-vaga/formulario-revisao.ts`

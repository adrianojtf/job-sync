# Tarefa 2.0: Equivalências e plano de adaptação no domínio

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Regra de negócio determinística que decide em quais experiências cada tecnologia equivalente entra. Sem IA.

<requirements>
- VOs `EquivalenciaTecnologia` (original e alvo obrigatórios e diferentes, sem diferenciar maiúsculas) e `AjusteTecnologia`.
- `DiretrizesExperiencia` (`trocar`, `manter`).
- `PlanoAdaptacao.distribuir(experiencias, equivalencias)`, `diretrizes(indice)`, `vazio()` e `ajustes`.
- Regras (PRD RF1 a RF4): descarta alvo já presente no perfil; uma ocorrência troca; duas ou mais trocam em todas menos a última, que mantém a original; comparação por palavra inteira, sem diferenciar maiúsculas, em cargo e descrição.
- Complexidade: medium. Dependências: 1.0.
</requirements>

## Subtarefas

- [x] 2.1 Testes dos VOs e da distribuição (Red).
- [x] 2.2 VOs.
- [x] 2.3 `PlanoAdaptacao`.

## Detalhes de Implementação

Ver "Regras de `PlanoAdaptacao.distribuir`" em `techspec-job-0037.md`.

## Critérios de Sucesso

- Todos os casos de distribuição da tech spec cobertos.
- O domínio não importa nada de adapters ou de infraestrutura (`test_arquitetura.py` verde).

## Testes da Tarefa

- [x] Uma, duas e três ocorrências; alvo já presente; "Java" não casa com "JavaScript"; experiência sem descrição; duas equivalências na mesma experiência; plano vazio.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/equivalencia_tecnologia.py` (novo)
- `src/jobsync/curriculo/domain/plano_adaptacao.py` (novo)
- `src/jobsync/curriculo/__init__.py`
- `src/jobsync/tests/curriculo/`

# Tarefa 5.0: Implementar use cases de candidatura (CriarCandidatura, MoverCandidatura, ListarCandidaturasPorStatus)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar os três casos de uso que sustentam o Kanban: criar uma candidatura a partir de uma vaga e um currículo salvo, mover entre status, e listar candidaturas agrupadas por status.

<requirements>
- `CriarCandidatura` recebe `perfil_identificador`, `vaga_id`, `curriculo_salvo_id`, `empresa`, `cargo`, cria a `Candidatura` com status inicial `APLICADO` e id/`data_aplicacao` gerados.
- `MoverCandidatura` aceita qualquer transição entre as quatro colunas (sem máquina de estados restritiva, conforme PRD) e atualiza a data da última mudança de status.
- `ListarCandidaturasPorStatus` retorna as candidaturas do perfil agrupadas por `StatusCandidatura` (ex: `dict[StatusCandidatura, tuple[Candidatura, ...]]`) — complexidade: medium.
</requirements>

## Subtarefas

- [x] 5.1 Criar `application/use_cases/criar_candidatura.py` com a classe `CriarCandidatura`.
- [x] 5.2 Criar `application/use_cases/mover_candidatura.py` com a classe `MoverCandidatura`.
- [x] 5.3 Criar `application/use_cases/listar_candidaturas_por_status.py` com a classe `ListarCandidaturasPorStatus`, agrupando por status.
- [x] 5.4 Escrever testes unitários para os três use cases usando fake de `RepositorioCandidaturaPort`.

## Detalhes de Implementação

Consultar a seção "Visão Geral dos Componentes" de `techspec-job-0006.md` e os requisitos funcionais 6-9 do `prd-job-0006.md`.

## Critérios de Sucesso

- Candidatura criada sempre começa em `APLICADO`.
- `MoverCandidatura` aceita qualquer transição entre colunas e persiste a mudança.
- `ListarCandidaturasPorStatus` agrupa corretamente as candidaturas do perfil por status, incluindo colunas vazias.

## Testes da Tarefa

- [x] Teste unitário: `CriarCandidatura` gera candidatura com status inicial `APLICADO`.
- [x] Teste unitário: `MoverCandidatura` atualiza o status e a data da última mudança.
- [x] Teste unitário: `ListarCandidaturasPorStatus` agrupa corretamente, incluindo status sem nenhuma candidatura.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `application/use_cases/criar_candidatura.py`
- `application/use_cases/mover_candidatura.py`
- `application/use_cases/listar_candidaturas_por_status.py`
- `tests/application/test_criar_candidatura.py`
- `tests/application/test_mover_candidatura.py`
- `tests/application/test_listar_candidaturas_por_status.py`

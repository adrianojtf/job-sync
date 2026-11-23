# Tarefa 1.0: Domínio de competências e campo `competencias` no rascunho

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cria o modelo de domínio de competências (categorias com tags) e o campo `competencias` em `RascunhoCurriculoAdaptado`, no mesmo padrão de `experiencias`. É domínio puro, sem I/O.

<requirements>
- `CategoriaCompetencia(nome, tags)` imutável, com `revisada` que aplica trim, descarta tag vazia e duplicada (sem diferenciar caixa) e devolve `None` para categoria sem nome ou sem tags.
- `de_texto` lê linhas "Rótulo: a, b" (aceita marcadores `-•*`); linha sem rótulo vai para a categoria "Tecnologias".
- `para_texto` gera "Rótulo: a, b", uma categoria por linha.
- `RascunhoCurriculoAdaptado.competencias` é opcional e exclusivo com a seção de texto `TECNOLOGIAS`.
- `para_curriculo` serializa as competências em uma seção `TECNOLOGIAS`, mantendo a ordem de exibição.
</requirements>

## Subtarefas

- [x] 1.1 Testes de `CategoriaCompetencia.revisada` (red).
- [x] 1.2 Testes de `de_texto`/`para_texto`: ida e volta, marcadores, linha sem rótulo, ":" no meio do texto (red).
- [x] 1.3 Testes do rascunho: exclusão mútua e `para_curriculo` (red).
- [x] 1.4 Implementar `curriculo/domain/competencias.py` (green).
- [x] 1.5 Alterar `rascunho_curriculo_adaptado.py` (green) e exportar pela API do pacote `curriculo`.
- [x] 1.6 Refatorar.

## Detalhes de Implementação

Techspec: "Interfaces Principais" e "Modelos de Dados". PRD: RF 1, 4 e 5 e casos extremos de tag duplicada e categoria vazia.

## Critérios de Sucesso

- Texto da IA vira categorias e volta a texto sem perda.
- Rascunho com competências e seção `TECNOLOGIAS` ao mesmo tempo é rejeitado.
- Nenhum teste existente do domínio de currículo quebra.

## Testes da Tarefa

- [x] Testes de unidade do domínio.
- [x] Regressão: `src/jobsync/tests/curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/competencias.py` (novo)
- `src/jobsync/curriculo/domain/rascunho_curriculo_adaptado.py`
- `src/jobsync/curriculo/domain/experiencia_adaptada.py` (padrão `revisada`)
- `src/jobsync/curriculo/__init__.py`
- `src/jobsync/tests/curriculo/`

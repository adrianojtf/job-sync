# Tarefa 2.0: Endpoint POST /curriculo/lacunas

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expõe as lacunas à tela: o router lê o perfil do usuário, monta o `HistoricoDoCandidato` e chama o caso de uso.

<requirements>
- `POST /curriculo/lacunas`: entrada `{descricao_vaga, cargo_alvo, idioma_alvo}`; saída `{lacunas: [{tema, pergunta}]}`.
- Schemas de request e response em `schemas/curriculo.py`; conversão de entidades para DTO no router.
- Perfil inexistente ou sem experiências devolve lista vazia; vaga vazia devolve 422.
- Injeção do caso de uso e do adapter em `dependencies.py`.
- Log informativo com o número de lacunas, sem texto de vaga ou perfil.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 2.1 Escrever os testes do router (red).
- [x] 2.2 Implementar os schemas, a injeção e o endpoint (green).
- [x] 2.3 Refatorar e rodar os testes de `entrypoints/api`.

## Detalhes de Implementação

Techspec: "Endpoints de API". PRD: RF 1, 3 e 12 (a tela pode pular a etapa). O contrato do `POST` de adaptação não muda.

## Critérios de Sucesso

- O endpoint devolve até 5 lacunas ou lista vazia, sem erro 5xx por falha da IA.
- O contrato de adaptação atual permanece igual.

## Testes da Tarefa

- [x] Testes do router com `TestClient` e IA falsa.
- [x] Regressão: `src/jobsync/tests/entrypoints/api/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/entrypoints/api/schemas/curriculo.py`
- `src/jobsync/entrypoints/dependencies.py`
- `src/jobsync/tests/entrypoints/api/test_routers.py`

## Resultado da execução

- `POST /v1/curriculos/lacunas` (corpo com `perfil_identificador`, `descricao_vaga`, `cargo_alvo`, `idioma_alvo`). O router monta o `HistoricoDoCandidato` a partir do perfil (`historico_do_candidato`) e o contexto com análise vazia, sem chamada extra de IA para analisar a vaga.
- 422 para perfil inexistente, vaga em branco ou idioma inválido.

# Tarefa 2.0: API do perfil: conquistas nos schemas e endpoint de conquistas parecidas

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expõe as conquistas no contrato do perfil, de forma retrocompatível, e cria o endpoint sem estado que avisa sobre conquistas parecidas.

<requirements>
- `ConquistaRequest` e `ConquistaResponse` (texto, origem) em `schemas/perfil_estruturado.py`.
- Os schemas de experiência (request e response) ganham `conquistas` opcional, padrão `[]`; payload antigo continua válido.
- Service `VerificarConquistasParecidas` em `perfil_estruturado/service_layer/verificar_conquistas_parecidas/` (`service.py`, `dtos.py`, `__init__.py`), com método `executar`.
- `POST /perfil-estruturado/conquistas/parecidas`: entrada `{texto, conquistas: [texto]}`, saída `{parecidas: [texto]}`; texto vazio devolve 422.
- O router converte entidades em DTO e não mapeia entidades direto para JSON.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 2.1 Escrever os testes dos schemas (red): com e sem `conquistas`, origem inválida.
- [x] 2.2 Escrever os testes de `VerificarConquistasParecidas` (red).
- [x] 2.3 Implementar schemas, service e DTOs (green).
- [x] 2.4 Escrever os testes do router (red): parecidas, nenhuma parecida, 422; `PUT` e `GET` do perfil com conquistas.
- [x] 2.5 Implementar o endpoint e a injeção em `dependencies.py` (green).
- [x] 2.6 Refatorar e rodar os testes de `perfil_estruturado` e `entrypoints/api`.

## Detalhes de Implementação

Techspec: "Endpoints de API" e "Decisões Principais" (endpoint sem estado). PRD: RF 2, 3 e 5. A API é a fonte do formulário do frontend (task 4.0).

## Critérios de Sucesso

- `PUT` e `GET` do perfil aceitam e devolvem conquistas, e o payload antigo continua funcionando.
- O endpoint devolve só as conquistas parecidas, sem consultar o banco.
- Nenhuma regressão nos testes da API do perfil.

## Testes da Tarefa

- [x] Testes de unidade do service e dos schemas.
- [x] Testes do router com `TestClient`.
- [x] Regressão: `src/jobsync/tests/perfil_estruturado/` e `src/jobsync/tests/entrypoints/api/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/schemas/perfil_estruturado.py`
- `src/jobsync/entrypoints/api/routers/perfil_estruturado_router.py`
- `src/jobsync/entrypoints/dependencies.py`
- `src/jobsync/perfil_estruturado/service_layer/verificar_conquistas_parecidas/ (novo)`
- `src/jobsync/tests/entrypoints/api/test_routers.py`

## Resultado da execução

- Schemas com `conquistas` opcional (origem validada por `Literal`), `VerificarConquistasParecidas` e `POST /perfil-estruturado/conquistas/parecidas`. Conquista duplicada na experiência devolve 422 ao salvar o perfil.
- Testes: `test_perfil_estruturado_conquistas_router.py` e `test_verificar_conquistas_parecidas_service.py`.

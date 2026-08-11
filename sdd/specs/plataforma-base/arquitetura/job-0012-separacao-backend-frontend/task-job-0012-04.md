# Tarefa 04: Implementar routers FastAPI v1 e documentação OpenAPI

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar os endpoints REST por domínio, garantindo contrato, códigos de status corretos e documentação interativa.

<requirements>
- Criar um router por domínio em `src/jobsync/entrypoints/api/routers/<dominio>_router.py`.
- Usar prefixo `/v1` e `tags` correspondentes aos domínios.
- Usar `response_model`, `status_code`, `summary` e `description` em cada path operation.
- Implementar exception handler central em `exceptions.py`.
- Tornar `/docs` e `/openapi.json` acessíveis em desenvolvimento.
</requirements>

## Subtarefas

- [ ] 4.1 Criar routers para domínios folha (`ats_score`, `token_captura`, `perfil`).
- [ ] 4.2 Criar routers para domínios de negócio (`vaga`, `candidatura`, `curriculo`, `vaga_externa`).
- [ ] 4.3 Implementar handler de exceções padronizado (formato único do projeto).
- [ ] 4.4 Adicionar exemplos em schemas (`json_schema_extra` / `Field(examples=...)`).
- [ ] 4.5 Validar endpoints com `TestClient`.

## Detalhes de Implementação

Ver `techspec-job-0012.md` -> Design de Implementação -> Endpoints de API. Seguir `back-end-general-rules.md` sobre REST e status codes.

## Critérios de Sucesso

- `/docs` carrega sem erros e agrupa endpoints por `tags`.
- Chamadas de exemplo retornam os status e corpos esperados.
- Exceções de domínio retornam respostas HTTP consistentes.

## Testes da Tarefa

- [ ] Testes com `TestClient` para todos os routers.
- [ ] Testes de códigos de erro (404, 422, 500).
- [ ] `pytest` e `lint-imports` passam.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/routers/`
- `src/jobsync/entrypoints/api/exceptions.py`
- `src/jobsync/entrypoints/api/main.py`
- `src/jobsync/entrypoints/api/dependencies.py`

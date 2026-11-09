# Tarefa 4.0: Endpoint POST /v1/candidaturas-ajustadas, handler 409 e coleção Postman

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expor o caso de uso pela API. O endpoint recebe os dados da vaga e o PDF em base64 e devolve a candidatura criada.

<requirements>
- Criar `CandidaturaConfirmarRequest` em `schemas/candidatura.py` com `perfil_identificador`, `cargo`, `empresa`, `descricao_vaga`, `nome_arquivo` e `pdf_base64`, com exemplo no `json_schema_extra`.
- `to_dto()` decodifica o base64; base64 inválido vira erro 422, não 500.
- Endpoint `POST /v1/candidaturas-ajustadas`, `status_code=201`, `response_model=CandidaturaResponse`, no `candidatura_router.py`, seguindo o estilo dos endpoints vizinhos.
- `ValueError` do caso de uso vira 422, como nos outros endpoints.
- Registrar em `exceptions.py` o handler de `LimiteCurriculosSalvosExcedido` com 409 no formato Problem Details e o texto do PRD: "Sua biblioteca de currículos está cheia. Remova um currículo para confirmar a candidatura."
- `POST /v1/curriculos` continua devolvendo 422 para a mesma condição (o router dele captura `ValueError` antes do handler global); não alterar esse comportamento.
- `ServiceConfirmarCandidaturaAjustadaDep` em `dependencies.py` com os três repositórios.
- Adicionar a requisição em `job-sync.postman_collection.json`.
- Nenhum endpoint existente muda de contrato.
</requirements>

## Subtarefas

- [ ] 4.1 Escrever os testes de router (red).
- [ ] 4.2 Criar o schema com a decodificação do base64.
- [ ] 4.3 Criar a injeção de dependência.
- [ ] 4.4 Criar o endpoint e o handler 409.
- [ ] 4.5 Atualizar a coleção Postman.
- [ ] 4.6 Teste com os repositórios SQLite em banco temporário (chaves estrangeiras de vaga e currículo).

## Detalhes de Implementação

Consultar em `techspec-job-0037.md` as seções "Endpoints de API" e "Considerações Técnicas > Decisões Principais". Seguir `.windsurf/rules/back-end-general-rules.md`.

## Critérios de Sucesso

- O endpoint cria a candidatura e ela aparece em `GET /v1/candidaturas` na coluna `APLICADO`.
- 409 com biblioteca cheia, com corpo Problem Details.
- 422 para campos vazios, PDF inválido e base64 inválido.
- Os testes existentes dos routers de candidatura e de currículo continuam passando.

## Testes da Tarefa

- [ ] 201 com o corpo da candidatura (status `APLICADO`, empresa, cargo, `curriculo_salvo_id`).
- [ ] A candidatura criada aparece na listagem do perfil e o currículo salvo aparece na biblioteca.
- [ ] 409 com biblioteca cheia e nada gravado.
- [ ] 422 com empresa vazia, PDF sem `%PDF` e base64 inválido.
- [ ] Com SQLite temporário, as chaves estrangeiras de vaga e currículo são aceitas.
- [ ] `POST /v1/curriculos` ainda devolve 422 com biblioteca cheia.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/schemas/candidatura.py`
- `src/jobsync/entrypoints/api/routers/candidatura_router.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/entrypoints/api/exceptions.py`
- `src/jobsync/tests/entrypoints/api/`
- `job-sync.postman_collection.json`

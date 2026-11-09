# Tarefa 2.0: Caso de uso MoverCandidatura com posição e endpoint de submissão

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

O caso de uso passa a aceitar a posição de destino e o endpoint existente expõe o campo opcional `posicao`. A mudança é compatível: quem não envia `posicao` coloca o cartão no topo.

<requirements>
- `MoverCandidatura.executar(candidatura_id, novo_status, posicao=None)`: busca a candidatura (404 se não existir), monta a coluna de destino, chama `reposicionar` e `aplicar_movimento`.
- `CandidaturaSubmeterRequest` ganha `posicao` opcional (inteiro >= 0); `CandidaturaResponse` ganha `posicao`.
- O router repassa `posicao` ao caso de uso; 404 e 422 como hoje.
- Log `INFO` por movimento (id, status de origem e destino, posição) e `WARNING` quando a posição é limitada ao fim da coluna, sem dados pessoais.
- Atualizar a coleção Postman com um exemplo com `posicao`.
- O uso do `MoverCandidatura` pelo Streamlit continua funcionando sem alteração.
</requirements>

## Subtarefas

- [ ] 2.1 Escrever os testes do caso de uso com repositório fake (red).
- [ ] 2.2 Implementar `executar` com `posicao` opcional e os logs.
- [ ] 2.3 Escrever os testes de schema e de router (`posicao` opcional, 422, resposta com `posicao`).
- [ ] 2.4 Ajustar schema, resposta e router.
- [ ] 2.5 Atualizar `job-sync.postman_collection.json`.

## Detalhes de Implementação

Techspec: "Interfaces Principais" (service), "Endpoints de API" e "Monitoramento e Observabilidade". PRD: RF2, RF5, RF7, RF9.

## Critérios de Sucesso

- Mover entre colunas e reordenar na mesma coluna funcionam pela API.
- Chamadas antigas (sem `posicao`) continuam válidas.
- `GET /v1/candidaturas` devolve cada coluna ordenada por `posicao`.

## Testes da Tarefa

- [ ] Caso de uso: mudança de coluna com posição, mesma coluna, posição omitida (topo), id inexistente.
- [ ] Router: 200 com `posicao`, 200 sem `posicao`, 404, 422 (posição negativa ou status inválido).
- [ ] Schemas: `posicao` opcional e presente na resposta.
- [ ] Regressão: `test_mover_candidatura_service.py`, `test_routers.py`, `test_schemas.py`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/candidatura/service_layer/mover_candidatura/service.py`
- `src/jobsync/entrypoints/api/schemas/candidatura.py`
- `src/jobsync/entrypoints/api/routers/candidatura_router.py`
- src/jobsync/entrypoints/streamlit_app.py (apenas conferir)
- `job-sync.postman_collection.json`
- `src/jobsync/tests/candidatura/test_mover_candidatura_service.py`
- `src/jobsync/tests/entrypoints/api/`

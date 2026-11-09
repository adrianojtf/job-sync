# Tarefa 6.0: API, Postman e tipos do frontend

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expor na API o cargo-alvo do contexto, o refino, o foco e os ajustes de tecnologia, sem quebrar clientes atuais.

<requirements>
- `ContextoVagaSchema.cargo_alvo` opcional (padrão "").
- `refino` opcional (`tentativa`, `sugestoes_anteriores`) nos três pedidos de sugestão; em `SugerirAjusteExperienciaRequest` (`extra="forbid"`) o campo precisa ser declarado.
- `foco` nas três respostas de sugestão.
- `ajustes_tecnologia` no rascunho de `/rascunhos-adaptados` (lista vazia por padrão); `/curriculos-revisados` não o exige.
- Pedidos antigos continuam válidos (200).
- Postman atualizado; `schema.d.ts` e `api/tipos` regenerados com Python 3.12.
- Complexidade: medium. Dependências: 4.0, 5.0.
</requirements>

## Subtarefas

- [x] 6.1 Testes de schema e router (Red).
- [x] 6.2 Schemas e conversões.
- [x] 6.3 Routers.
- [x] 6.4 Postman.
- [x] 6.5 Tipos do frontend.

## Detalhes de Implementação

Ver "Modelos de Dados" e "Endpoints de API" em `techspec-job-0037.md`.

## Critérios de Sucesso

- Cada endpoint coberto em 200 (com e sem campos novos), 422 e 502.
- Passo de contrato do CI verde.

## Testes da Tarefa

- [x] Testes de schema e router; verificação do contrato gerado.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/{schemas/curriculo.py,routers/curriculo_router.py}`
- `src/jobsync/tests/entrypoints/api/`
- `job-sync.postman_collection.json`
- `frontend/src/api/`

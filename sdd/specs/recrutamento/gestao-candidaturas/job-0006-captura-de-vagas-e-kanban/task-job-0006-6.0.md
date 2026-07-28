# Tarefa 6.0: Implementar ServidorCaptura (FastAPI)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o servidor HTTP local separado (FastAPI) que recebe a captura da extensão de navegador, autentica via token opaco e delega ao use case `CapturarVaga`.

<requirements>
- Endpoint único: `POST /api/vagas/capturar`, corpo `{"texto": str, "url": str}`, header `Authorization: Bearer <token>`.
- Resolver `perfil_identificador` a partir do token via uma nova tabela/consulta `token_captura` (reaproveitando `RepositorioSqlite` da Tarefa 3.0).
- Retornar `201` com o id da vaga criada em caso de sucesso, `401` se o token for inválido, `422` se o payload não tiver `texto` — complexidade: medium.
- Adicionar `fastapi` e `uvicorn` a `requirements.txt`.
</requirements>

## Subtarefas

- [x] 6.1 Adicionar `fastapi` e `uvicorn` a `requirements.txt` e instalar no `.venv-local`.
- [x] 6.2 Criar `infrastructure/api/servidor_captura.py` com o app FastAPI e o endpoint `POST /api/vagas/capturar`.
- [x] 6.3 Implementar a resolução de token → perfil (usando a tabela `token_captura`) e o uso de `CapturarVaga`.
- [x] 6.4 Escrever testes de serviço usando `TestClient` do FastAPI, cobrindo sucesso (201), token inválido (401) e payload sem texto (422).
- [x] 6.5 Documentar no `README-macos.md` o novo passo de execução (`uvicorn infrastructure.api.servidor_captura:app --port 8502`).

## Detalhes de Implementação

Consultar as seções "Design de Implementação > Endpoints de API" e "Pontos de Integração" de `techspec-job-0006.md`.

## Critérios de Sucesso

- O endpoint aceita uma captura válida e persiste a vaga associada ao perfil correto.
- Token inválido é rejeitado com 401, sem vazar detalhes de outros perfis.

## Testes da Tarefa

- [x] Teste de serviço: captura com token válido retorna 201 e persiste a vaga.
- [x] Teste de serviço: captura com token inválido retorna 401.
- [x] Teste de serviço: captura sem campo `texto` retorna 422.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `infrastructure/api/servidor_captura.py`
- `requirements.txt`
- `README-macos.md`
- `tests/infrastructure/api/test_servidor_captura.py`

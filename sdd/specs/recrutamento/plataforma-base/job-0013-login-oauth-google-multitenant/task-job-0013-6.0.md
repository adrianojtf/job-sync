# Tarefa 6.0: Routers de autenticação, cookie, middleware de origem e login simples

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expor os serviços das tarefas 4.0 e 5.0 pela API, com cookie de sessão, proteção contra CSRF e tratamento de erros em RFC 7807. Complexidade: high.

<requirements>
- Endpoints da tabela "Endpoints de API" da Tech Spec, com os status indicados.
- Cookie `js_sessao`: `HttpOnly`, `SameSite=Lax`, `Path=/`, `Secure` conforme `AUTH_COOKIE_SECURE`.
- Cookie curto `js_oauth` no início do fluxo Google.
- Erros do callback viram `302` para `/entrar?erro=<codigo>` com lista fixa de códigos.
- Middleware que recusa (403) métodos de escrita com `Origin` fora das origens permitidas.
- `UsuarioAutenticadoDep` (401 sem sessão válida).
- Handlers para `NaoAutenticado` (401), `AcessoNegado` (403) e `LimiteTentativasExcedido` (429), no formato já usado em `exceptions.py`.
- `POST /sessoes/simples` e a opção `simples` em `GET /provedores` só existem com `AUTH_LOGIN_SIMPLES_HABILITADO=true`.
- `cors.py` aceita credenciais quando `CORS_ORIGINS` lista origens explícitas.
- Registrar routers em `main.py` e fábricas em `dependencies.py`.
</requirements>

## Subtarefas

- [ ] 6.1 Schemas Pydantic e fábricas de dependências.
- [ ] 6.2 Router de sessões, usuários, confirmações e redefinições de senha.
- [ ] 6.3 Router de provedores (autorização e retorno).
- [ ] 6.4 Middleware de origem, `UsuarioAutenticadoDep` e handlers de erro.
- [ ] 6.5 Login simples atrás da flag e ajuste de CORS.
- [ ] 6.6 Testes com `TestClient` (padrão de `tests/entrypoints/api`).

## Detalhes de Implementação

Ver "Endpoints de API" e "Pontos de Integração" em `techspec-job-0013.md`. Seguir os routers existentes (`perfil_router.py`, `token_captura_router.py`) e `back-end-general-rules.md`.

## Critérios de Sucesso

- Fluxos de cadastro, confirmação, login, logout e redefinição funcionam de ponta a ponta nos testes.
- Cookie sai com os atributos esperados; logout o invalida.
- Escrita com `Origin` estranha recebe 403.
- Sem a flag, `POST /sessoes/simples` devolve 404.

## Testes da Tarefa

- [ ] Testes de API com `TestClient` e serviços fake

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/routers/{sessao,usuario,provedor}_router.py`
- `src/jobsync/entrypoints/api/{main,cors,dependencies,exceptions}.py`
- `src/jobsync/entrypoints/dependencies.py`
- `src/jobsync/entrypoints/api/schemas/`
- `src/jobsync/tests/entrypoints/api/`

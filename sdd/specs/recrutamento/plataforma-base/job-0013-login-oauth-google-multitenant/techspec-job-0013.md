# Especificação Técnica

## Resumo Executivo

Esta Tech Spec implementa o PRD `prd-job-0013.md`: login com Google (OAuth 2.0 / OpenID Connect, Authorization Code + PKCE conduzido pelo backend) e login com e-mail e senha, ambos terminando na mesma **sessão por cookie HttpOnly guardada no PostgreSQL**. Um novo domínio `autenticacao` guarda `Usuario`, identidades externas, credencial de senha, sessões e tokens de uso único. O `Perfil` e seu identificador natural (`perfil_identificador`) não mudam: cada `Usuario` aponta para exatamente um `Perfil`, e todos os dados atuais continuam amarrados a ele.

Dois pontos centram o desenho. Primeiro, **o vínculo de perfis legados usa o mesmo caminho do cadastro novo**: o mantenedor cria um `Usuario` com o e-mail do dono, e o primeiro login com esse e-mail verificado conclui o vínculo. Segundo, **as rotas existentes hoje confiam no `perfil_identificador` vindo do cliente** (25 ocorrências nos routers). Elas passam a exigir sessão e a conferir se o perfil pedido é o da sessão, sem mudar o contrato das rotas.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Componentes novos, em `src/jobsync/autenticacao/`:

| Camada | Componente | Responsabilidade |
|---|---|---|
| domain | `Usuario`, `IdentidadeExterna`, `Sessao`, `TokenUsoUnico`, `EstadoOAuth` | Entidades e invariantes (e-mail normalizado, expiração) |
| domain | `Email`, `Senha` (value objects) | Normalização do e-mail; política de senha |
| domain | `UsuarioRepository`, `SessaoRepository`, `TokenUsoUnicoRepository`, `EstadoOAuthRepository`, `LimiteTentativasRepository` | Portas de persistência |
| domain | `ProvedorIdentidade`, `HasherSenha`, `EnviadorEmail` | Portas externas |
| service_layer | `IniciarLoginOAuth`, `ConcluirLoginOAuth` | Fluxo Google |
| service_layer | `CadastrarUsuario`, `ConfirmarEmail`, `EntrarComSenha`, `SolicitarRedefinicaoSenha`, `RedefinirSenha` | Fluxo e-mail/senha |
| service_layer | `ResolverSessao`, `EncerrarSessao`, `AssociarEmailAPerfil` | Sessão e migração |
| adapters | `ProvedorGoogle`, `HasherSenhaArgon2`, `EnviadorEmailSmtp`, `EnviadorEmailLog`, `*RepositoryImpl`, `*RepositoryFake` | Implementações |

Componentes existentes alterados:

- `entrypoints/api/main.py`: registra os novos routers e o middleware de verificação de origem.
- `entrypoints/api/dependencies.py` e `entrypoints/dependencies.py`: fábricas dos novos serviços e as dependências `UsuarioAutenticadoDep` e `exigir_acesso_ao_perfil`.
- `entrypoints/api/exceptions.py`: mapeia `NaoAutenticado` (401), `AcessoNegado` (403) e `LimiteTentativasExcedido` (429) para RFC 7807.
- `entrypoints/api/cors.py`: passa a aceitar credenciais quando `CORS_ORIGINS` lista origens explícitas.
- Todos os routers com `perfil_identificador` (candidatura, curriculo, perfil, perfil_estruturado, token_captura, vaga): chamam `exigir_acesso_ao_perfil`. `vaga_externa_router` fica fora, pois usa token de captura.
- `perfil_router.py` (`GET /perfis/{id}`): deixa de criar perfil; devolve o perfil da sessão ou 403.
- `shared_kernel/adapters/persistence/migracoes/0003_autenticacao.sql` (nova migração).
- Frontend: `shared/sessao/SessaoProvider.tsx`, `features/entrar/EntrarPage.tsx`, `api/http-api-client.ts`, `app/guardas.tsx`, `app/rotas.tsx` e novas páginas.
- `entrypoints/cli/associar_email_perfil.py` (novo), `docker-compose.yml`, `.env.example`, `README.md`.

### Fluxo de dados

**Google:** `GET /v1/provedores/google/autorizacao` gera `state`, `nonce` e `code_verifier`, grava o hash do `state` em `estado_oauth`, define o cookie curto `js_oauth` (HttpOnly) e redireciona ao Google. Em `.../retorno`, o serviço confere cookie e `state`, troca o `code` com `code_verifier`, valida o ID token e resolve o usuário. Depois cria a sessão e redireciona ao frontend.

**Resolução da identidade** (`ConcluirLoginOAuth`):
1. Existe `identidade_externa(google, sub)`: usa o usuário dela.
2. Senão, o ID token precisa ter `email_verified = true`; sem isso, recusa.
3. Existe `usuario` com esse e-mail: cria a identidade, marca `email_verificado = true` e **descarta os links de confirmação pendentes** (que carregariam uma senha escolhida antes da verificação).
4. Senão, cria `Perfil` (identificador `u-` + 12 hex aleatórios, sem dado pessoal em URL ou log), `Usuario` e identidade, na mesma transação.

A identidade é a dupla `(provedor, sub)`, nunca o e-mail. Isso responde à questão 8 do PRD: mudar o e-mail no Google não quebra o vínculo, e o `usuario.email` não é atualizado sozinho.

## Design de Implementação

### Interfaces Principais

```python
class ProvedorIdentidade(Protocol):
    nome: str
    def url_autorizacao(self, estado: str, nonce: str, code_challenge: str) -> str: ...
    def trocar_codigo(self, codigo: str, code_verifier: str, nonce: str) -> IdentidadeAutenticada: ...

@dataclass(frozen=True)
class IdentidadeAutenticada:
    provedor: str
    subject: str
    email: str
    email_verificado: bool
    nome: str | None

class HasherSenha(Protocol):
    def gerar(self, senha: str) -> str: ...
    def conferir(self, senha: str, hash_: str) -> bool: ...

class EnviadorEmail(Protocol):
    def enviar(self, para: Email, assunto: str, corpo: str) -> None: ...
```

Provedores ficam num dicionário `{nome: ProvedorIdentidade}` injetado. Adicionar um provedor é criar um adapter e registrá-lo, sem tocar nas regras de vínculo (RF 22).

### Modelos de Dados

Migração `0003_autenticacao.sql`:

```sql
CREATE TABLE usuario (
    id UUID PRIMARY KEY,
    email TEXT NOT NULL,
    email_verificado BOOLEAN NOT NULL DEFAULT FALSE,
    nome TEXT,
    perfil_identificador TEXT NOT NULL UNIQUE REFERENCES perfil(identificador),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX ux_usuario_email ON usuario (lower(email));
CREATE TABLE identidade_externa (
    provedor TEXT NOT NULL, subject TEXT NOT NULL,
    usuario_id UUID NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    PRIMARY KEY (provedor, subject));
CREATE TABLE credencial_senha (
    usuario_id UUID PRIMARY KEY REFERENCES usuario(id) ON DELETE CASCADE,
    senha_hash TEXT NOT NULL, atualizada_em TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE sessao (
    token_hash BYTEA PRIMARY KEY,
    usuario_id UUID NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    criada_em TIMESTAMPTZ NOT NULL, ultimo_acesso_em TIMESTAMPTZ NOT NULL,
    expira_em TIMESTAMPTZ NOT NULL);
CREATE TABLE token_uso_unico (
    token_hash BYTEA PRIMARY KEY,
    usuario_id UUID NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    finalidade TEXT NOT NULL CHECK (finalidade IN ('confirmacao_email','redefinicao_senha')),
    expira_em TIMESTAMPTZ NOT NULL, usado_em TIMESTAMPTZ,
    carga TEXT);
CREATE TABLE estado_oauth (
    estado_hash BYTEA PRIMARY KEY, provedor TEXT NOT NULL,
    code_verifier TEXT NOT NULL, nonce TEXT NOT NULL,
    destino TEXT NOT NULL, expira_em TIMESTAMPTZ NOT NULL);
CREATE TABLE limite_tentativa (
    chave TEXT PRIMARY KEY, contagem INT NOT NULL,
    janela_inicia_em TIMESTAMPTZ NOT NULL, bloqueado_ate TIMESTAMPTZ);
```

Tokens de sessão e de uso único têm 256 bits (`secrets.token_urlsafe(32)`) e **só o hash SHA-256 vai ao banco**; um vazamento do banco não entrega sessões válidas.

### Endpoints de API

Prefixo `/v1`. Rotas de recurso, conforme `back-end-general-rules.md`.

| Método e caminho | Função | Resposta |
|---|---|---|
| `GET /provedores` | Métodos de entrada disponíveis (`google`, `senha`, `simples`) | 200 |
| `GET /provedores/{provedor}/autorizacao?destino=` | Inicia OAuth | 302 |
| `GET /provedores/{provedor}/retorno` | Callback; cria sessão | 302 para `/` ou `/entrar?erro=<codigo>` |
| `POST /usuarios` | Cadastro (e-mail, senha) | 202 sempre, sem revelar se o e-mail existe |
| `PUT /confirmacoes-email/{token}` | Confirma e-mail | 204 |
| `POST /sessoes` | Login por e-mail e senha | 201 + `Set-Cookie` |
| `DELETE /sessoes/atual` | Logout | 204 |
| `GET /usuarios/me` | Usuário e `perfil_identificador` da sessão | 200 / 401 |
| `POST /redefinicoes-senha` | Pede link de redefinição | 202 sempre |
| `PUT /redefinicoes-senha/{token}` | Define nova senha; encerra todas as sessões | 204 |
| `POST /sessoes/simples` | Login legado (RF 23); **só existe com `AUTH_LOGIN_SIMPLES_HABILITADO=true`** | 201 |

Cookie de sessão `js_sessao`: `HttpOnly`, `SameSite=Lax`, `Path=/`, `Secure` quando `AUTH_COOKIE_SECURE=true` (desligado só em `http://localhost`). O redirecionamento pós-login só aceita `destino` que comece com `/` e não com `//`, o que evita redirecionamento aberto.

## Pontos de Integração

- **Google OIDC** ([documentação](https://developers.google.com/identity/openid-connect/openid-connect)): escopos `openid email profile`; endpoints de autorização, token e chaves públicas (JWKS) do Google. O adapter valida assinatura via JWKS, `iss`, `aud` (= client id), `exp` e `nonce`. Em erro de rede ou resposta inválida, o fluxo termina em `/entrar?erro=provedor_indisponivel`, sem expor detalhe.
- **SMTP** via `smtplib` da stdlib, configurado por `SMTP_HOST/PORT/USER/PASSWORD/FROM`. Em desenvolvimento, `EnviadorEmailLog` registra o link, e o `docker-compose` ganha um Mailpit opcional (perfil `dev`).
- **Google Cloud Console** (manual): cliente OAuth tipo "Aplicativo da Web", URIs de redirecionamento `http://localhost:8080/v1/provedores/google/retorno` e `http://localhost:8000/v1/provedores/google/retorno`. Para aceitar qualquer conta Google, a tela de consentimento deve ser do tipo **Externo**. Premissa a confirmar no console: o status "Em produção" (e não "Teste") é o que libera contas fora da lista de testadores.

Variáveis novas: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `AUTH_BASE_URL_FRONTEND`, `AUTH_COOKIE_SECURE`, `AUTH_SESSAO_INATIVIDADE_DIAS`, `AUTH_SESSAO_MAXIMA_DIAS`, `AUTH_LOGIN_SIMPLES_HABILITADO`, `SMTP_*`. Nada disso vai ao repositório (`.env.example` leva só placeholders).

## Abordagem de Testes

Segue `testing-rules.md`: sem comentários, blocos AAA, classes `TestNomeDaClasse`, mocks só de serviços externos.

### Testes Unidade

Com fakes dos repositórios (padrão `*_repository_fake.py`), relógio injetado e um `ProvedorIdentidade` fake:

- `ConcluirLoginOAuth`: identidade já vinculada; e-mail verificado que vincula a usuário legado; e-mail **não** verificado recusado; usuário novo cria perfil; links de confirmação pendentes descartados no vínculo.
- `CadastrarUsuario`: resposta idêntica para e-mail novo e existente; senha fora da política rejeitada.
- `EntrarComSenha`: erro genérico para e-mail desconhecido, senha errada e conta sem senha ativada (e-mail ainda não confirmado); bloqueio após N falhas. A mensagem genérica orienta a confirmar o e-mail, sem confirmar a existência da conta.
- `ResolverSessao`: expiração por inatividade e absoluta; renovação do último acesso.
- `RedefinirSenha`: token usado ou expirado falha; todas as sessões do usuário são apagadas.
- `exigir_acesso_ao_perfil`: perfil igual passa, diferente gera `AcessoNegado`.

### Testes de Serviço

- Repositórios Postgres contra o banco de teste do `conftest.py`, incluindo unicidade de e-mail sem diferenciar maiúsculas e `ON DELETE CASCADE`.
- `ProvedorGoogle` com `httpx.MockTransport`: ID token com `aud`, `iss`, `exp` ou `nonce` errados, assinatura inválida e `email_verified = false`.
- Routers com `TestClient`: cada rota existente devolve 401 sem sessão e 403 com perfil de outro usuário; cookie com os atributos esperados; requisição de escrita com `Origin` estranha recebe 403.
- Frontend (Vitest): `EntrarPage`, páginas de cadastro, confirmação e redefinição; `SessaoProvider` com 401. E2E (Playwright) usa o login simples ligado por configuração.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Migração `0003`, entidades e value objects (`Email`, `Senha`), com testes.
2. Portas e repositórios (fake e Postgres).
3. Adapters `HasherSenhaArgon2`, `EnviadorEmail*` e `ProvedorGoogle`.
4. Serviços de sessão e de e-mail/senha, depois o fluxo OAuth.
5. Routers de autenticação, cookie, middleware de origem e handlers de erro.
6. `UsuarioAutenticadoDep` e `exigir_acesso_ao_perfil` aplicados a todos os routers existentes, com testes de 401/403. Fica antes do frontend para fechar o buraco de segurança primeiro.
7. CLI `associar_email_perfil` e rotina de migração do mantenedor.
8. Frontend: sessão por `GET /usuarios/me`, nova `EntrarPage`, páginas de cadastro, confirmação e redefinição, tratamento global de 401.
9. `docker-compose`, `.env.example`, README, E2E e validação manual com credenciais Google reais.

### Dependências Técnicas

- Novas bibliotecas (fixar versões ao implementar): `argon2-cffi` (hash) e `PyJWT[crypto]` (validação de ID token via JWKS). HTTP usa o `httpx` já existente.
- Cliente OAuth criado no Google Cloud pelo mantenedor.
- Servidor SMTP (ou Mailpit local) para cadastro e redefinição.

## Monitoramento e Observabilidade

Logs estruturados no padrão atual (`logging`), sempre com `usuario_id`, nunca com senha, token, `code` ou e-mail completo:

- INFO: `login_sucesso` (método), `usuario_criado`, `vinculo_realizado` (provedor), `sessao_encerrada`, `senha_redefinida`.
- WARNING: `login_falha` (motivo genérico, chave de limite em hash), `login_bloqueado`, `oauth_estado_invalido`, `token_uso_unico_invalido`.
- ERROR: falha ao falar com o Google ou com o SMTP.

Os dois contadores do PRD (logins por método e vínculos de perfis legados) saem desses eventos.

## Considerações Técnicas

### Decisões Principais

- **Sessão opaca no Postgres em vez de JWT:** permite logout e redefinição de senha derrubarem sessões na hora. JWT exigiria lista de revogação. Alinhado ao [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html).
- **Argon2id para senhas**, com os parâmetros-padrão da biblioteca, conforme o [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) e a [RFC 9106](https://www.rfc-editor.org/rfc/rfc9106). Política: mínimo de 10 e máximo de 128 caracteres, sem regras de composição e com lista embutida de senhas comuns, na linha do [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html).
- **PKCE + `state` + `nonce`** ([RFC 7636](https://www.rfc-editor.org/rfc/rfc7636)), com `state` amarrado ao navegador pelo cookie `js_oauth`, contra login CSRF.
- **CSRF:** `SameSite=Lax` mais checagem de `Origin` em métodos de escrita ([OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)). Token duplo (double submit) foi descartado por ora: a API é JSON, e a checagem de origem cobre o caso sem custo no frontend.
- **Vínculo por e-mail verificado e senha ativada só na confirmação:** impede o pré-sequestro, em que um atacante cadastra a senha no e-mail da vítima antes dela. O cadastro não grava a credencial: o hash da senha vai na `carga` do token de confirmação e só vira credencial quando o e-mail é confirmado (e só se a conta ainda não estava verificada). Um cadastro novo invalida o link anterior. Assim não há "credencial não confirmada" para remover no vínculo com o Google; o vínculo apenas descarta os links de confirmação pendentes.
- **`Perfil` intacto:** nenhuma tabela de dados é migrada; só se acrescenta `usuario` apontando para `perfil`. Rollback é descartar a migração `0003`.
- **Padrões de prazo (premissas, configuráveis):** sessão expira com 7 dias de inatividade e 30 dias no máximo; confirmação de e-mail vale 24 h; redefinição vale 1 h; bloqueio após 5 falhas por e-mail em 15 min (também por IP).

### Riscos Conhecidos

- **IP atrás do nginx:** sem `--proxy-headers` no uvicorn, o limite por IP enxerga o IP do nginx. Mitigação: configurar proxy confiável; até lá, o limite por e-mail é o efetivo.
- **Bloqueio por e-mail permite negar acesso a um terceiro** (DoS de conta). Mitigação: bloqueio curto e progressivo, e o Google não é afetado.
- **Rota esquecida sem proteção:** mitigada pelo teste que percorre todas as rotas do `app.routes` e exige 401 sem sessão, exceto a lista explícita de rotas públicas.
- **Produção com origens separadas:** exigirá `SameSite`/domínio de cookie e CORS com credenciais revistos. Não faz parte desta entrega (PRD), e o desenho não bloqueia.
- **Cadastro por e-mail depende de SMTP funcional;** sem ele, o usuário não consegue ativar a conta. Google segue como alternativa.

### Conformidade com Padrões

- `code-design-standards.md`: novo domínio `autenticacao` com `domain`, `service_layer` e `adapters`; referências entre domínios apenas por ID (`Usuario` guarda `perfil_identificador`, sem importar `Perfil`).
- `back-end-general-rules.md`: recursos no plural e sem verbos, status específicos (201, 202, 204, 401, 403, 429), erros em RFC 7807, Pydantic nos contratos.
- `testing-rules.md`: ver "Abordagem de Testes".
- **Desvio justificado:** as rotas existentes recebem 401/403 novos e `GET /perfis/{id}` deixa de criar perfil. A regra pede alteração de contrato só quando solicitada, e o PRD (RF 20, 21 e 23) solicita. Os parâmetros e corpos não mudam.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/plataforma-base/job-0013-login-oauth-google-multitenant/prd-job-0013.md`
- `sdd/specs/recrutamento/plataforma-base/job-0004-persistencia-perfil-e-login-simples/` (login atual)
- `src/jobsync/perfil/` e `src/jobsync/token_captura/`
- `src/jobsync/entrypoints/api/{main,cors,dependencies,exceptions}.py` e `routers/*.py`
- `src/jobsync/entrypoints/dependencies.py`
- `src/jobsync/shared_kernel/adapters/persistence/migracoes/` e `shared_kernel/domain/relogio.py`
- `frontend/src/{shared/sessao,features/entrar,api,app}/`, `frontend/e2e/`
- `docker-compose.yml`, `frontend/nginx.conf.template`, `.env.example`, `requirements-backend.txt`

## Questões em Aberto

Premissas assumidas por recomendação, por não terem sido respondidas. Confirmar ou corrigir:

1. Bibliotecas `argon2-cffi` e `PyJWT[crypto]` aprovadas como novas dependências.
2. SMTP: qual provedor real será usado fora do ambiente local.
3. Prazos de sessão, de links e de bloqueio (valores acima).
4. Lista de senhas comuns embutida basta, ou o projeto deve consultar um serviço de senhas vazadas?
5. O status da tela de consentimento do Google que libera qualquer conta ("Em produção") precisa de verificação do app para os escopos `openid email profile`? Não tenho certeza. Conferir no console antes da entrega.
6. `perfil_identificador` de usuários novos como `u-<hex>`: aceitável, ou prefere derivado do e-mail?

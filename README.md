# Adaptador de Currículo para Vagas (MVP)

Sistema de gestão de currículo e candidatura. Recebe um currículo em PDF,
uma descrição de vaga, e gera uma nova versão do currículo adaptada
(seção por seção) para aquela vaga, no idioma escolhido (Português/Inglês).

## Arquitetura

O projeto segue **Arquitetura Hexagonal (Ports and Adapters)** com **DDD**, com as
regras de negócio isoladas de qualquer framework ou biblioteca externa:

```
src/                        Código fonte da aplicação
  jobsync/                  Raiz do pacote da aplicação
    <dominio>/              Cada domínio de negócio encapsula suas próprias camadas
      domain/               Entidades, Value Objects, Ports (interfaces) - DENTRO do hexágono
      service_layer/        Casos de uso e DTOs - DENTRO do hexágono
      adapters/             Adapters concretos (implementações das portas) - FORA do hexágono

    shared_kernel/          Conceitos transversais compartilhados entre domínios
      domain/               Value Objects compartilhados (ex: NomeArquivo, CatalogoLocalizacao)
      adapters/             Mecanismos técnicos compartilhados (ex: ClienteOpenAI, ClienteJev, pool PostgreSQL e migrações)

    entrypoints/            Adapters de entrada da aplicação
      streamlit_app.py      Interface web (Streamlit)
      servidor_captura.py   API FastAPI para captura de vagas (extensão Chrome)
      dependencies.py       Composition Root / injeção de dependências

    tests/                  Testes unitários e de arquitetura espelhando src/jobsync/
      <dominio>/            Testes do domínio correspondente
      shared_kernel/        Testes dos conceitos transversais
      test_arquitetura.py   Validação dos contratos do import-linter
      e2e/app_e2e.py        API real com dublês de IA, usada pelos testes E2E da UI

storage/                    PDFs gerados são salvos aqui (os dados ficam no PostgreSQL)
frontend/                   Nova interface web (React + Vite + TypeScript), cliente da API /v1
sdd/                        Documentos de especificação e templates
```

**Fluxo de processamento por seção:** o PDF enviado é lido e segmentado pela
IA em seções reconhecidas (Tecnologias, Perfil, Experiências, Formação,
Certificações, Idiomas). Cada seção é então enviada individualmente à IA
para ser reescrita/priorizada conforme a vaga e traduzida para o idioma
alvo, preservando os fatos originais (empresas, datas, tecnologias). As
seções ajustadas são remontadas e um novo PDF é gerado.

## Pré-requisitos

- Python 3.10+
- PostgreSQL 15 ou superior (testado no 15.3 e no 16)
- Uma chave da OpenAI: https://platform.openai.com/api-keys
- Uma chave da TypeSafe AI (Jev) para as avaliações: https://docs.typesafe.ai/

## Instalação

O projeto usa um ambiente virtual padrão do Python. No Linux/macOS, prefira `python3`; no Windows, use `python`.

```bash
# 1. Criar o ambiente virtual
python -m venv venv          # Linux/macOS também aceitam .venv
# Windows: python -m venv venv

# 2. Ativar o ambiente
source venv/bin/activate     # Linux/macOS
# Windows: venv\Scripts\activate

# 3. Atualizar o pip e instalar as dependências
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Copiar o arquivo de variáveis de ambiente
cp .env.example .env
# Edite o .env e substitua pelas suas chaves da OpenAI e da TypeSafe AI
```

> No macOS, veja também `README-macos.md` para instruções específicas.

## Variáveis de ambiente (.env)

Após copiar `.env.example` para `.env`, o arquivo mínimo fica assim:

```env
# .env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-6-luna
TYPESAFE_API_KEY=sua_chave_aqui
TYPESAFE_MODEL=jev-1.14.0
DATABASE_URL=postgresql://job_sync:troque_a_senha@localhost:5432/job_sync
```

Os valores são carregados em tempo de execução por `python-dotenv`; certifique-se de que o arquivo esteja na raiz do projeto.

- `OPENAI_API_KEY` / `OPENAI_MODEL`: provedor de geração de texto (extração, adaptação de seções, carta de apresentação e sugestões ATS). O modelo padrão é `gpt-6-luna`.
- `DATABASE_URL`: conexão com o PostgreSQL. Obrigatória: sem ela a API não sobe. As tabelas são criadas e atualizadas sozinhas na subida (migrações em `shared_kernel/adapters/persistence/migracoes/`).
- `TYPESAFE_API_KEY` / `TYPESAFE_MODEL`: provedor de avaliações estruturadas (Jev). Sem essa chave, as avaliações automáticas ficam indisponíveis, mas a adaptação do currículo continua funcionando.
- Variáveis de login (`GOOGLE_*`, `AUTH_*`, `SMTP_*`): veja a seção [Autenticação](#autenticação-google-e-e-mail-e-senha).

## Autenticação (Google e e-mail e senha)

Todas as rotas de dados exigem sessão. A pessoa entra com a conta Google ou com e-mail e senha, e a
API entrega um cookie `js_sessao` (HttpOnly, `SameSite=Lax`). Cada usuário tem um único perfil e só
acessa os próprios dados: sem sessão a API responde 401; com o perfil de outra pessoa, 403.

### Login com Google

1. No [Google Cloud Console](https://console.cloud.google.com/apis/credentials), crie um **ID do cliente OAuth**
   do tipo "Aplicativo da Web".
2. Em "URIs de redirecionamento autorizados", cadastre `<AUTH_BASE_URL_FRONTEND>/v1/provedores/google/retorno`
   (local: `http://localhost:8080/v1/provedores/google/retorno`; sem o Nginx, `http://localhost:8000/...`).
3. Na tela de consentimento, escolha o tipo de usuário **Externo** para aceitar qualquer conta Google
   (Gmail e Workspace) e use os escopos `openid`, `email` e `profile`. Enquanto o app estiver em modo
   "Teste", só contas listadas como testadoras conseguem entrar; confira no console o que é exigido
   para publicá-lo.
4. Preencha `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` no `.env`. Sem eles o botão não aparece.

O fluxo usa Authorization Code com PKCE, `state` e `nonce`, conduzido pelo backend. O e-mail só vale
se o Google o informar como verificado.

### Login com e-mail e senha

O cadastro envia um link de confirmação; **a senha só passa a valer depois de confirmar o e-mail**.
Sem `SMTP_HOST`, os e-mails só aparecem no log da API (útil em desenvolvimento). Para ver os e-mails
numa caixa de entrada local:

```bash
docker compose --profile dev up --build   # sobe também o Mailpit
# no .env: SMTP_HOST=mailpit  SMTP_PORT=1025  SMTP_STARTTLS=false
```

A caixa de entrada fica em `http://localhost:8025`. Senhas têm de 10 a 128 caracteres e são
guardadas com Argon2id. Cinco falhas seguidas bloqueiam a conta por 15 minutos.

### Migrando um perfil criado antes da autenticação

Perfis antigos eram só um identificador. Para que o dono continue com os dados, associe o e-mail dele
ao perfil (com `DATABASE_URL` configurada):

```bash
PYTHONPATH=src python -m jobsync.entrypoints.cli.associar_email_perfil --perfil meu-identificador --email dono@exemplo.com
```

O comando **não libera acesso sozinho**: o vínculo se completa no primeiro login em que o dono prova
o e-mail (Google com e-mail verificado, ou o link de confirmação por e-mail). Assim, saber o
identificador de um perfil antigo não basta para tomá-lo. Repetir o mesmo par não altera nada.
Códigos de saída: 0 sucesso, 2 dados inválidos, 3 banco inacessível, 4 conflito (perfil ou e-mail
já associados a outro usuário). Perfis antigos sem e-mail associado continuam no banco, mas
inacessíveis por login.

### Login por identificador (somente desenvolvimento)

`AUTH_LOGIN_SIMPLES_HABILITADO=true` habilita `POST /v1/sessoes/simples` e um campo na tela de
entrada, sem senha. Serve para desenvolvimento, testes e para a coleção Postman. **Nunca ligue em
produção.**

### Atrás de um proxy

O limite de tentativas por IP precisa do IP real. Com o Nginx do compose, `AUTH_CABECALHO_IP_CLIENTE`
já vem como `X-Forwarded-For` (vale a última entrada, a que o proxy acrescenta). Sem proxy, deixe em
branco. Em produção, sirva por HTTPS e use `AUTH_COOKIE_SECURE=true`. Se frontend e API ficarem em
origens diferentes, liste as origens em `CORS_ORIGINS` (com origens explícitas o CORS aceita o cookie).

## Banco de dados (PostgreSQL)

Crie o usuário e o banco uma vez (como superusuário do Postgres):

```bash
psql -U postgres -c "CREATE USER job_sync WITH PASSWORD 'troque_a_senha'"
psql -U postgres -c "CREATE DATABASE job_sync OWNER job_sync"
```

Datas são guardadas em `TIMESTAMPTZ` (UTC) e a API as devolve com o fuso (`...Z`). O navegador
mostra cada data no fuso do próprio usuário.

### Migrando os dados do SQLite antigo

Antes desta versão, os dados ficavam em `storage/job_sync.db`. O arquivo **não é alterado** pela
migração e serve de backup. Com a API parada e `DATABASE_URL` configurada:

```bash
PYTHONPATH=src python -m jobsync.entrypoints.cli.migrar_sqlite_para_postgres --sqlite storage/job_sync.db --dry-run
PYTHONPATH=src python -m jobsync.entrypoints.cli.migrar_sqlite_para_postgres --sqlite storage/job_sync.db
```

- `--dry-run` faz tudo e desfaz no final, só para conferir o relatório.
- As datas antigas não guardavam fuso. Elas são lidas no fuso local da máquina; use
  `--fuso-origem America/Sao_Paulo` (ou outro) para informar o fuso correto.
- O comando só roda em banco vazio, grava tudo ou nada e confere contagens, hash dos PDFs e a ordem
  do board. Códigos de saída: 0 sucesso, 2 problema na origem, 3 destino inválido, 4 divergência.
- Candidaturas que apontam para um currículo salvo já removido são migradas assim mesmo e listadas
  em "Avisos" (o sistema sempre permitiu remover currículos em uso, e a tela lida com isso).
- Se a origem tiver outras referências órfãs, datas ou JSON inválidos, o comando lista todos os problemas e
  não grava nada. Se for um banco muito antigo (sem a coluna `posicao`), abra-o uma vez com a versão
  anterior do sistema e repita.

Para voltar ao SQLite, use a versão anterior do sistema com o arquivo `storage/job_sync.db`; o que
foi gravado no PostgreSQL depois da troca não volta sozinho.

## Executando o MVP

```bash
PYTHONPATH=src streamlit run src/jobsync/entrypoints/streamlit_app.py
```

A interface abrirá em `http://localhost:8501`. Anexe o PDF do currículo,
cole a descrição da vaga, informe cargo e empresa, escolha o idioma e
clique em "Gerar currículo adaptado".

### Servidor de captura de vagas (extensão Chrome)

A funcionalidade de captura de vagas depende de um segundo processo, rodando
em paralelo ao Streamlit:

```bash
PYTHONPATH=src uvicorn jobsync.entrypoints.servidor_captura:app --port 8502
```

Esse servidor expõe `http://localhost:8502/api/vagas/capturar` e é usado
exclusivamente pela extensão do navegador.

### Servidor backend API (FastAPI)

Para subir o backend independente com documentação OpenAPI em `/docs`:

```bash
PYTHONPATH=src uvicorn jobsync.entrypoints.api.main:app --reload --port 8000
```

O backend fica disponível em `http://localhost:8000` e a documentação interativa
em `http://localhost:8000/docs`.

#### Endpoints de avaliação (Jev)

Além dos recursos existentes, a API expõe avaliações estruturadas via Jev, com
score geral de 0 a 100 e resultados por dimensão (score, nível e confiança):

- `POST /v1/vagas/avaliacoes` — avalia a descrição da vaga nas dimensões
  completude, clareza, relevância e inclusão. O texto não é persistido.
- `POST /v1/experiencias-profissionais/avaliacoes` — avalia uma experiência
  individual em relação a uma vaga-alvo nas dimensões clareza de escrita,
  qualidade/detalhe, aderência à vaga e consistência textual. O texto não é
  persistido nem alterado.

`POST /v1/curriculos/{id}/adaptacoes` também executa a avaliação da vaga antes
de adaptar e devolve os resultados em campos aditivos (`avaliacao_vaga`,
`status_avaliacao_vaga`, `avaliacoes_experiencias`). Quando a entrada vem de um
perfil estruturado, cada experiência é adaptada e avaliada individualmente;
para entrada somente em PDF, não há avaliação automática individual das
experiências. Um score baixo nunca bloqueia a adaptação e, se o Jev estiver
indisponível, o fluxo prossegue e sinaliza as avaliações como `indisponivel`.

Limitações: a dimensão `consistencia_textual` mede apenas coerência e
sustentação interna do texto — não é verificação factual externa.

## Leitura de vaga por link (JOB-0047)

As telas "Ajustar para uma vaga" e "Colar vaga" (vagas salvas) têm o campo **Link da vaga**. A pessoa
cola o link, clica em "Ler vaga" e o sistema preenche título, empresa, local (na captura) e descrição.
O resultado é um **rascunho**: nada é salvo até a pessoa confirmar, e os campos seguem editáveis.

| Fonte | Como é lida |
|---|---|
| LinkedIn | Versão pública da vaga (a que um visitante sem login vê). Aceita links diretos (`/jobs/view/...`) e de busca com `currentJobId`. |
| Gupy, Greenhouse, Lever e páginas de carreira | Dados estruturados `JobPosting` (JSON-LD). Sem eles, o texto da página vai para a IA identificar os campos. |
| Texto colado | A IA identifica cargo, empresa e demais campos; a descrição é o texto original, sem resumo. |

O link é normalizado antes de ser usado ou salvo: parâmetros de rastreamento (por exemplo, `trk` e
`utm_*` de um e-mail do LinkedIn) saem e o link do LinkedIn vira `https://www.linkedin.com/jobs/view/<id>/`.

Se o site bloquear a leitura, a vaga não existir ou a página não tiver dados, a mensagem orienta a
**colar o texto da vaga**, e o botão "Preencher os campos pelo texto" faz o mesmo preenchimento. A leitura
nunca impede a pessoa de concluir o fluxo.

- Endpoint: `POST /v1/vagas/extracoes` com `{ "url": "...", "texto": "..." }` (pelo menos um; o texto tem
  prioridade). Responde 200 com o rascunho, 422 (link inválido ou fonte desativada), 429 (limite de uso, com
  `Retry-After`) ou 502 (leitura indisponível). Não persiste nada.
- Variáveis (veja `.env.example`):
  - `VAGA_LEITURA_LINKEDIN_HABILITADA` (padrão `true`): com `false`, links do LinkedIn pedem para colar o texto.
  - `VAGA_LEITURA_LIMITE_POR_MINUTO` (10) e `VAGA_LEITURA_LIMITE_POR_DIA` (100): limites por pessoa, por processo da API.
  - `VAGA_LEITURA_TIMEOUT_SEGUNDOS` (15): tempo máximo de cada leitura.
- A captura passou a guardar `cargo`, `empresa` e `local` da vaga (colunas opcionais da migração `0005`).
- Segurança: o servidor só acessa endereços públicos `http`/`https`. Endereços internos (`localhost`, redes
  privadas, metadados de nuvem) são recusados em cada redirecionamento, e há limite de redirecionamentos,
  tamanho e tempo (`shared_kernel/adapters/cliente_http_seguro.py`).

**Limitações e riscos do LinkedIn.** O acesso à versão pública da vaga não é documentado pelo LinkedIn, pode
mudar ou ser bloqueado sem aviso (resposta 429 ou desafio anti-bot, mais provável a partir de IPs de servidor),
e os termos de uso do LinkedIn proíbem acesso automatizado. O sistema faz uma única requisição por link, não usa
login nem cookies, não repete a requisição após um bloqueio e não tenta contorná-lo. Avalie o risco antes de manter
a fonte ligada e acompanhe a taxa de sucesso pelos logs do logger `jobsync.vaga` (campos `fonte`, `dominio` e
`motivo`; o conteúdo da vaga não é registrado).

## Frontend (nova interface web)

A nova UI fica em `frontend/` (JOB-0015). É uma SPA em React 18 + Vite + TypeScript que consome
apenas a API `/v1`. O Streamlit continua disponível enquanto a transição acontece.

Pré-requisitos: Node.js 20.19+ (ou 22.13+) e o backend rodando na porta 8000.

```bash
cd frontend
npm ci
npm run dev        # http://localhost:5173 (proxy de /v1 para http://localhost:8000)
```

| Comando | O que faz |
|---|---|
| `npm run dev` | Servidor de desenvolvimento. `VITE_API_PROXY` muda o destino do proxy `/v1`. |
| `npm test` | Testes de unidade e de componentes (Vitest + Testing Library + MSW). |
| `npm run lint` | ESLint e Prettier. |
| `npm run build` | Checagem de tipos e build de produção em `dist/`. |
| `npm run gerar-tipos` | Regenera `src/api/schema.d.ts` a partir do OpenAPI do backend (`OPENAPI_URL`, padrão `http://localhost:8000/openapi.json`). |
| `npm run e2e` | Fluxos ponta a ponta e acessibilidade (Playwright + axe). Sobe sozinho a API de teste e a UI. |

**Contrato da API:** sempre que um schema do backend mudar, rode `npm run gerar-tipos` com o
backend atualizado e faça commit do `schema.d.ts`. O CI falha se o arquivo estiver desatualizado.

**Testes E2E:** usam a API real (PostgreSQL, casos de uso e geração de PDF) com dublês apenas nas
portas de IA (`src/jobsync/tests/e2e/app_e2e.py`), então não precisam de chaves. Na primeira vez,
instale o navegador com `npx playwright install chromium`. O Python usado é `python3`, ou o
definido em `E2E_PYTHON` (ex.: `E2E_PYTHON=venv/bin/python npm run e2e`), com as dependências de
`requirements.txt` instaladas. O banco do E2E vem de `E2E_DATABASE_URL` (padrão
`postgresql://localhost:5432/job_sync_e2e`, que precisa existir).

O app de E2E também simula o Google (uma "tela do Google" local que devolve o código ao callback real), uma
caixa de e-mail em memória e a criação de um perfil antigo, para o navegador percorrer o login
completo, inclusive a migração de um perfil legado. Ele liga `AUTH_LOGIN_SIMPLES_HABILITADO` só para os
testes prepararem dados.

**Variáveis:** `VITE_API_BASE_URL` (opcional) aponta a UI para outra origem da API. Vazio, a UI usa
a mesma origem: o proxy do Vite em desenvolvimento e o Nginx no container. Se a UI e a API
estiverem em origens diferentes, inclua a origem da UI em `CORS_ORIGINS` no `.env` do backend.

## Rodando os testes (TDD)

O `pytest.ini` já configura os caminhos (`pythonpath = . src src/jobsync`), então basta rodar a partir da raiz do projeto:

```bash
pytest
```

Comandos úteis:

```bash
pytest -q                            # saída resumida
pytest -v                            # verboso
pytest src/jobsync/tests/curriculo   # testes de um domínio
pytest -k "tailor"                   # filtrar por nome de teste
```

Se preferir explicitar o `PYTHONPATH`:

```bash
PYTHONPATH=src pytest
```

Os testes de repositório, de API e da migração de dados usam um PostgreSQL real. Crie um banco
vazio de teste e aponte `TEST_DATABASE_URL` para ele (sem a variável, esses testes são ignorados
ou falham, conforme o caso):

```bash
createdb job_sync_test
TEST_DATABASE_URL=postgresql://job_sync:troque_a_senha@localhost:5432/job_sync_test pytest
```

Os testes de `domain/` e `service_layer/` são independentes de rede e de
chave de API (usam dublês de teste / fakes para as portas). Os testes de
adapters de PDF também não dependem de rede.

## Deploy com Docker

Para executar o backend de forma isolada, sem depender do Streamlit:

```bash
# 1. Construir a imagem
docker build -t job-sync-backend .

# 2. Subir o container
docker run -p 8000:8000 job-sync-backend
```

O backend estará disponível em `http://localhost:8000`, com documentação
interativa em `/docs` e health check em `/health`.

Para passar as chaves da OpenAI/TypeSafe ou outras variáveis de ambiente:

```bash
cp .env.example .env
# edite o .env com seus valores
docker run --env-file .env -p 8000:8000 job-sync-backend
```

### Backend e frontend juntos (docker compose)

```bash
cp .env.example .env   # opcional: chaves da OpenAI e da TypeSafe
docker compose up --build
```

A UI fica em `http://localhost:8080` e a API em `http://localhost:8000`. No container do
frontend, o Nginx serve os arquivos estáticos, devolve o `index.html` nas rotas da SPA e encaminha
`/v1` para o backend (`API_UPSTREAM`, padrão `http://backend:8000`), com timeout de 180 s para as
chamadas de IA e limite de 10 MB por requisição (PDFs de até 5 MB em base64). Os PDFs gerados
ficam em `./storage`.

O banco é o PostgreSQL **instalado na máquina hospedeira**, fora do compose. O backend o alcança por
`host.docker.internal` (`DATABASE_URL` no `docker-compose.yml`; ajuste usuário e senha). No
hospedeiro, o Postgres precisa escutar na interface da bridge do Docker (`listen_addresses` no
`postgresql.conf`) e aceitar a rede do container (`pg_hba.conf`, por exemplo `host job_sync job_sync
172.16.0.0/12 scram-sha-256`).

## Lint de arquitetura

```bash
PYTHONPATH=src lint-imports
```

## Padrão de nome do arquivo gerado

```
nomeCompleto-AAAA-MM-DD-cargoDaVaga-empresa.pdf
```

Exemplo: `AdrianoJoaoTeixeiraFilho-2026-07-22-EngenheiroDeSoftwareSenior-TechCorp.pdf`

Os arquivos são salvos automaticamente em `storage/` além de disponíveis
para download pela interface.

## Limitações conhecidas do MVP

- Depende das APIs da OpenAI e da TypeSafe AI (requer internet e chaves de
  API); não é totalmente offline.
- A segmentação de seções depende da qualidade da extração de texto do
  PDF original — currículos com layout muito incomum ou PDFs escaneados
  (imagem sem OCR) podem não ser segmentados corretamente.
- O layout do PDF gerado é fixo (não é uma cópia do PDF original), gerado
  via reportlab a partir do conteúdo estruturado extraído.

# Tarefa 10.0: Infra, documentação, E2E e validação manual

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Fechar a entrega: configuração de ambiente, documentação, testes de ponta a ponta e validação manual do fluxo Google e da migração do perfil legado. Complexidade: medium.

<requirements>
- `docker-compose.yml` com Mailpit opcional (perfil `dev`) e variáveis novas repassadas ao backend.
- `.env.example` com placeholders de `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `AUTH_*` e `SMTP_*`; nenhum segredo real.
- README: configuração do cliente OAuth no Google Cloud (URIs de redirecionamento), variáveis, uso da CLI de migração e login simples em desenvolvimento.
- E2E Playwright atualizados para usar o login simples habilitado por configuração; novo cenário de cadastro e confirmação via Mailpit ou log.
- Coleção Postman atualizada com as novas rotas (se o projeto a mantém).
- Validação manual: login com Google real, vínculo do perfil legado pela CLI, logout, redefinição de senha, tentativa de acesso a dados de outro perfil.
- Conferir no Google Cloud Console o tipo de tela de consentimento (Externo) e a necessidade de verificação do app (questão 5 da Tech Spec).
- Suíte completa (`pytest`, `lint-imports`, `npm test`) verde.
</requirements>

## Subtarefas

- [x] 10.1 `docker-compose.yml` e `.env.example`.
- [x] 10.2 README e coleção Postman.
- [x] 10.3 Atualizar e ampliar os E2E.
- [x] 10.4 Rodar a suíte completa.
- [ ] 10.5 Roteiro de validação manual e registro do resultado.

## Detalhes de Implementação

Ver "Pontos de Integração", "Sequenciamento de Desenvolvimento" e "Questões em Aberto" em `techspec-job-0013.md`.

## Resultado da execução

Verificado nesta execução (banco PostgreSQL local, sem dublês na autenticação):

- `pytest` 1293 passando, `lint-imports` com 3 contratos mantidos, Vitest 354, `npm run lint`, `npm run build` e Playwright 53 de 53.
- E2E novos (`frontend/e2e/autenticacao.spec.ts`, 10 cenários): cadastro, confirmação, login, logout, cookie HttpOnly, redefinição de senha, destino pós-login, Google simulado (inclusive e-mail não verificado), perfil legado vinculado pelo e-mail do dono, isolamento entre usuários e CSRF.
- Validação manual contra a API de produção (roteiro com `curl`): 401 sem sessão, 403 com perfil alheio, hash Argon2id no banco, nenhum token em texto puro (sessões e links), bloqueio com 429 e `Retry-After` após 5 falhas, CLI de associação (sucesso, idempotência, conflito = 4, perfil inexistente = 2) e a tentativa de tomar o perfil legado cadastrando o e-mail do dono (continua sem acesso).

Achados corrigidos durante a execução:

- O limite de tentativas por IP virava um balde global atrás do Nginx (todos chegam com o IP do proxy): 5 falhas de qualquer pessoa bloqueariam o login de todos. Agora o IP real vem de `AUTH_CABECALHO_IP_CLIENTE` e o limite por IP é mais folgado (30) que o da conta (5).
- Corrida que já existia em `useFontesCurriculo`: se a lista de PDFs chegasse antes do perfil mestre, o formulário travava no PDF. O padrão só é definido com as duas consultas prontas (causava um E2E intermitente).

## PENDENTE (depende de credenciais e acesso que esta execução não tem)

- [ ] 10.5 Validar o login com o **Google real**: criar o cliente OAuth, cadastrar as URIs de redirecionamento, preencher `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` e entrar com uma conta de verdade. Nos testes, o Google é simulado (a troca de código e a validação do ID token são testadas com rede simulada, nunca contra o Google).
- [ ] Rodar a CLI `associar_email_perfil` no banco de verdade com o e-mail do dono e confirmar o vínculo no primeiro login com Google.
- [ ] Conferir no Google Cloud Console o tipo da tela de consentimento (Externo), se o status "Em produção" é exigido para contas fora da lista de testadores e se os escopos `openid email profile` exigem verificação do app (questão 5 da Tech Spec).
- [ ] Testar o envio real de e-mail (SMTP) fora do ambiente local.

## Critérios de Sucesso

- Ambiente local sobe com `docker compose` e login funciona nos dois métodos.
- Perfil legado do mantenedor acessível após o primeiro login com Google.
- Nenhum segredo no repositório.

## Testes da Tarefa

- [x] Suíte completa de backend e frontend
- [x] E2E Playwright

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `docker-compose.yml`, `.env.example`, `README.md`
- `frontend/e2e/`
- `job-sync.postman_collection.json`

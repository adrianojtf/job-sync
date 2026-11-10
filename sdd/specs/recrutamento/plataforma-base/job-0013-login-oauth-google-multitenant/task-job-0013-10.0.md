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

- [ ] 10.1 `docker-compose.yml` e `.env.example`.
- [ ] 10.2 README e coleção Postman.
- [ ] 10.3 Atualizar e ampliar os E2E.
- [ ] 10.4 Rodar a suíte completa.
- [ ] 10.5 Roteiro de validação manual e registro do resultado.

## Detalhes de Implementação

Ver "Pontos de Integração", "Sequenciamento de Desenvolvimento" e "Questões em Aberto" em `techspec-job-0013.md`.

## Critérios de Sucesso

- Ambiente local sobe com `docker compose` e login funciona nos dois métodos.
- Perfil legado do mantenedor acessível após o primeiro login com Google.
- Nenhum segredo no repositório.

## Testes da Tarefa

- [ ] Suíte completa de backend e frontend
- [ ] E2E Playwright

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `docker-compose.yml`, `.env.example`, `README.md`
- `frontend/e2e/`
- `job-sync.postman_collection.json`

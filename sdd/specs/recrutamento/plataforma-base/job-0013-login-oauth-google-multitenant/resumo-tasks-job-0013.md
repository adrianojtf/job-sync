# Resumo de Tarefas de Implementação do Login V2 (Google e e-mail/senha)

## Tarefas

- [x] 1.0 Migração `0003_autenticacao.sql`, entidades de domínio e value objects
- [x] 2.0 Portas e repositórios (fake e Postgres) do domínio `autenticacao`
- [x] 3.0 Adapters externos: `HasherSenhaArgon2`, `EnviadorEmail*` e `ProvedorGoogle`
- [x] 4.0 Serviços de sessão e de e-mail/senha
- [x] 5.0 Serviços do fluxo Google (`IniciarLoginOAuth`, `ConcluirLoginOAuth`)
- [x] 6.0 Routers de autenticação, cookie de sessão, middleware de origem e login simples atrás de flag
- [ ] 7.0 Proteger os routers existentes por sessão e perfil
- [ ] 8.0 CLI `associar_email_perfil` para migrar perfis legados
- [ ] 9.0 Frontend: sessão por cookie, nova tela de entrada e fluxos de e-mail
- [ ] 10.0 Infra, documentação, E2E e validação manual

## Dependências

- 1.0 antes de 2.0.
- 2.0 antes de 3.0, 4.0, 5.0 e 8.0 (podem andar em paralelo entre si; 4.0 e 5.0 usam fakes das portas).
- 3.0, 4.0 e 5.0 antes de 6.0.
- 6.0 antes de 7.0.
- 6.0 e 7.0 antes de 9.0.
- 7.0, 8.0 e 9.0 antes de 10.0.

## Complexidade

| Tarefa | Complexidade |
|---|---|
| 1.0 | medium |
| 2.0 | medium |
| 3.0 | high |
| 4.0 | high |
| 5.0 | high |
| 6.0 | high |
| 7.0 | high |
| 8.0 | low |
| 9.0 | high |
| 10.0 | medium |

## Entregáveis principais

- Domínio `autenticacao` com usuários, identidades externas, credencial de senha, sessões e tokens de uso único.
- Login com Google (Authorization Code + PKCE) e com e-mail e senha, ambos gerando sessão por cookie HttpOnly.
- Todas as rotas de dados exigem sessão e só aceitam o perfil do usuário autenticado.
- Vínculo seguro de perfis legados por e-mail verificado, com CLI para o mantenedor.
- Frontend com tela de entrada, cadastro, confirmação de e-mail e redefinição de senha.
- Login simples por identificador restrito a desenvolvimento e testes, atrás de flag.

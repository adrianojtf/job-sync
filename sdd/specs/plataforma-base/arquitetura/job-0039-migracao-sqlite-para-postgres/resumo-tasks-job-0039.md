# Resumo de Tarefas de Implementação da Migração de SQLite para PostgreSQL (JOB-0039)

## Tarefas

- [ ] 1.0 Base de conexão e schema no PostgreSQL
- [ ] 2.0 Repositórios simples: perfil, token de captura e vaga
- [ ] 3.0 Repositórios com tipos especiais: currículo salvo e perfil estruturado
- [ ] 4.0 Repositório de candidatura: posição do board e concorrência
- [ ] 5.0 Raiz de composição, lifespan da API e remoção do SQLite do runtime
- [ ] 6.0 Núcleo da migração de dados SQLite para PostgreSQL
- [ ] 7.0 CLI de migração de dados
- [ ] 8.0 Configuração e documentação
- [ ] 9.0 E2E e CI completo
- [ ] 10.0 Ensaio e troca real dos dados

## Dependências

- 1.0 não depende de nenhuma outra tarefa.
- 2.0, 3.0, 4.0 e 6.0 dependem só da 1.0 e podem ser feitas em paralelo.
- 2.0, 3.0 e 4.0 mudam os construtores dos repositórios e deixam a raiz de composição quebrada até a 5.0. Mantê-las na mesma branch e só integrar depois da 5.0.
- 5.0 depende de 2.0, 3.0 e 4.0.
- 7.0 depende de 6.0.
- 8.0 depende de 5.0 e 7.0.
- 9.0 depende de 5.0.
- 10.0 depende de 7.0, 8.0 e 9.0 e é executada manualmente pelo responsável pela operação.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Base de conexão e schema no PostgreSQL | medium | — | Executor: aplica pendentes na ordem, ignora aplicadas, respeita rollback do chamador. |
| 2.0 | Repositórios simples: perfil, token de captura e vaga | low | 1.0 | `test_perfil_repository_impl`, `test_token_captura_repository_impl`, `test_vaga_repository_impl` sobre Postgres real. |
| 3.0 | Repositórios com tipos especiais: currículo salvo e perfil estruturado | medium | 1.0 | `test_curriculo_salvo_repository_impl` e `test_perfil_estruturado_repository_impl` sobre Postgres real. |
| 4.0 | Repositório de candidatura: posição do board e concorrência | high | 1.0 | `test_candidatura_repository_impl` completo sobre Postgres real. |
| 5.0 | Raiz de composição, lifespan da API e remoção do SQLite do runtime | medium | 2.0, 3.0, 4.0 | Subida sem `DATABASE_URL` falha com mensagem sem senha. |
| 6.0 | Núcleo da migração de dados SQLite para PostgreSQL | high | 1.0 | Conversões puras sem banco. |
| 7.0 | CLI de migração de dados | medium | 6.0 | Testes de ponta a ponta da CLI com origem SQLite temporária e Postgres real. |
| 8.0 | Configuração e documentação | low | 5.0, 7.0 | `docker compose config` válido. |
| 9.0 | E2E e CI completo | medium | 5.0 | Suíte Playwright completa. |
| 10.0 | Ensaio e troca real dos dados | low | 7.0, 8.0, 9.0 | Validação manual dos fluxos listados; não há teste automatizado. |

## Entregáveis principais

- Aplicação executando inteiramente sobre PostgreSQL, com pool de conexões e migrações versionadas.
- CLI de migração dos dados atuais, com dry-run, validação por contagem e hash, e tudo ou nada.
- Documentação de instalação, troca e retorno, e CI com testes de repositório e E2E sobre Postgres real.

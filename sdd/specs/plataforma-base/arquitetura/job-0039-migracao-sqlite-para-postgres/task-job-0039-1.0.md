# Tarefa 1.0: Base de conexão e schema no PostgreSQL

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cria a base que todas as outras tarefas usam: dependências, pool de conexões, migrações versionadas, fixture de teste e serviço Postgres no CI.

<requirements>
- Adicionar `psycopg[binary]` e `psycopg-pool` (série 3.2, versão exata validada com Python 3.12) a `requirements.txt` e `requirements-backend.txt`.
- `conexao_postgres.py` cria o `ConnectionPool` a partir de `DATABASE_URL`, falha rápido sem a variável ou sem conexão e mascara a senha nos logs (RF-03, RF-04).
- `executor_migracoes.py` aplica as migrações pendentes dentro da transação do chamador, sem commit, e registra versões em `schema_migrations` (RF-05).
- `migracoes/0001_schema_inicial.sql` com as seis tabelas, conforme a tabela de tipos da Tech Spec.
- Fixture em `tests/conftest.py`: lê `TEST_DATABASE_URL`, aplica migrações uma vez por sessão, faz `TRUNCATE ... CASCADE` entre testes e usa `skip` com mensagem clara quando a variável não existe.
- Serviço `postgres:16` com healthcheck e `TEST_DATABASE_URL` no job `lint-and-test` do CI.
</requirements>

## Subtarefas

- [ ] 1.1 Escrever testes do executor de migrações (ordem, idempotência, rollback do chamador) e da máscara de senha (red).
- [ ] 1.2 Implementar `conexao_postgres.py` e `executor_migracoes.py`.
- [ ] 1.3 Escrever `0001_schema_inicial.sql` e um teste que confere tabelas, colunas e tipos criados.
- [ ] 1.4 Criar a fixture de pool e limpeza em `conftest.py`.
- [ ] 1.5 Atualizar requirements e o job `lint-and-test` do CI.

## Detalhes de Implementação

Techspec: "Componentes", "Modelos de Dados", "Testes de Integração" e "Dependências Técnicas". PRD: RF-03, RF-04, RF-05.

## Critérios de Sucesso

- Migrações rodam duas vezes sem erro e sem duplicar o registro.
- Sem `DATABASE_URL`, a criação do pool falha com mensagem sem senha.
- Os testes de integração rodam no CI contra o Postgres.

## Testes da Tarefa

- [ ] Executor: aplica pendentes na ordem, ignora aplicadas, respeita rollback do chamador.
- [ ] Máscara de senha da URL.
- [ ] Schema criado com os tipos esperados (`BYTEA`, `JSONB`, `BOOLEAN`, `TIMESTAMP`).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/shared_kernel/adapters/persistence/conexao_postgres.py` (novo)
- `src/jobsync/shared_kernel/adapters/persistence/migracoes/` (novo)
- `src/jobsync/tests/conftest.py` (novo ou alterado)
- `requirements.txt`, `requirements-backend.txt`
- `.github/workflows/ci.yml`

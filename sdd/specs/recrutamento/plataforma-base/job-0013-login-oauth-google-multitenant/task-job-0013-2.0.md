# Tarefa 2.0: Portas e repositórios (fake e Postgres) do domínio `autenticacao`

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Definir as portas do domínio e implementar, para cada repositório, um fake em memória (usado nos testes de serviço) e a implementação PostgreSQL. Complexidade: medium.

<requirements>
- Portas de persistência: `UsuarioRepository`, `SessaoRepository`, `TokenUsoUnicoRepository`, `EstadoOAuthRepository`, `LimiteTentativasRepository`.
- Portas externas: `ProvedorIdentidade`, `HasherSenha`, `EnviadorEmail` (e `IdentidadeAutenticada`).
- Tokens de sessão e de uso único guardados apenas como hash SHA-256.
- Criar usuário, perfil e identidade na mesma transação quando o serviço pedir.
- E-mail único sem diferenciar maiúsculas e minúsculas.
- Atualizar `conftest.py` para truncar as novas tabelas.
</requirements>

## Subtarefas

- [ ] 2.1 Criar as portas em `autenticacao/domain/` (padrão de `perfil/domain/perfil_repository.py`).
- [ ] 2.2 Escrever testes de contrato reutilizáveis para os repositórios e implementar os fakes.
- [ ] 2.3 Implementar os `*RepositoryImpl` com `psycopg_pool.ConnectionPool` e testes de integração.
- [ ] 2.4 Atualizar `src/jobsync/tests/conftest.py` com as novas tabelas.

## Detalhes de Implementação

Ver "Interfaces Principais" e "Modelos de Dados" em `techspec-job-0013.md`. Seguir `perfil/adapters/perfil_repository_impl.py` e `perfil_repository_fake.py`.

## Critérios de Sucesso

- Fake e implementação Postgres passam pelo mesmo conjunto de testes de contrato.
- Nenhum token em texto puro chega ao banco.
- Apagar um usuário apaga identidades, credenciais, sessões e tokens (cascata).

## Testes da Tarefa

- [ ] Testes de unidade dos fakes
- [ ] Testes de integração dos repositórios Postgres

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/autenticacao/domain/*_repository.py`
- `src/jobsync/autenticacao/adapters/*_repository_impl.py`
- `src/jobsync/autenticacao/adapters/*_repository_fake.py`
- `src/jobsync/tests/conftest.py`
- `src/jobsync/tests/autenticacao/`

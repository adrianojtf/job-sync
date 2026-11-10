# Tarefa 5.0: Raiz de composição, lifespan da API e remoção do SQLite do runtime

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Liga a aplicação ao pool, aplica as migrações na subida e remove o código SQLite do runtime.

<requirements>
- `obter_pool_conexoes` (singleton) substitui `obter_caminho_banco`; `obter_repositorio_*` passam o pool; remover `JOB_SYNC_DB_PATH` e `DATABASE_PATH`.
- `lifespan` em `api/main.py`: cria o pool, aplica migrações (commit) e fecha o pool no desligamento; falha clara sem a variável (RF-04).
- Log `INFO` na subida: host, porta, banco, tamanho do pool e migrações aplicadas, sem usuário e senha.
- Remover `_conexao_sqlite.py` e `CaminhoBancoDep`.
- Ajustar `test_seguranca_dependencias.py` e `test_candidaturas_ajustadas_router.py` (trocar `PRAGMA foreign_key_check` por contagens SQL).
</requirements>

## Subtarefas

- [ ] 5.1 Escrever testes da composição e do `lifespan` (red).
- [ ] 5.2 Implementar pool singleton e ajustar `dependencies.py`.
- [ ] 5.3 Implementar o `lifespan` e os logs.
- [ ] 5.4 Remover `_conexao_sqlite.py`, `CaminhoBancoDep` e referências a `sqlite3` fora da CLI.
- [ ] 5.5 Ajustar os testes de API e rodar `lint-imports`.

## Detalhes de Implementação

Techspec: "Visão Geral dos Componentes", "Monitoramento e Observabilidade" e "Conformidade com Padrões". PRD: RF-01, RF-03, RF-04, RF-05.

## Critérios de Sucesso

- A API sobe e responde a todos os endpoints existentes sobre Postgres.
- Nenhum `import sqlite3` no código de produção fora de `migracao_sqlite.py`.
- `lint-imports` e a suíte `pytest` completa passam.

## Testes da Tarefa

- [ ] Subida sem `DATABASE_URL` falha com mensagem sem senha.
- [ ] Suíte completa de API e services.
- [ ] `test_arquitetura.py` e `lint-imports`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/dependencies.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/entrypoints/api/main.py`
- `src/jobsync/shared_kernel/adapters/persistence/_conexao_sqlite.py` (remover)
- `src/jobsync/tests/entrypoints/api/test_seguranca_dependencias.py`
- `src/jobsync/tests/entrypoints/api/test_candidaturas_ajustadas_router.py`
- `src/jobsync/tests/test_arquitetura.py`

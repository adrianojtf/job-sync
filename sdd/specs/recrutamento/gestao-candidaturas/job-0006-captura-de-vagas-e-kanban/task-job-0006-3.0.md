# Tarefa 3.0: Estender RepositorioSqlite com as tabelas vaga, candidatura, token_captura

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Estender `infrastructure/persistence/repositorio_sqlite.py` (Fase 0) para também implementar `RepositorioVagaPort` e `RepositorioCandidaturaPort`, reaproveitando a mesma conexão/arquivo `storage/job_sync.db`.

<requirements>
- Adicionar as tabelas `token_captura`, `vaga` e `candidatura` ao schema (`CREATE TABLE IF NOT EXISTS`), preservando as tabelas já existentes (`perfil`, `curriculo_salvo`).
- `candidatura` deve incluir uma coluna para a data da última mudança de status (ex: `data_ultima_mudanca_status`), usada para reconstruir `historico_status` como uma tupla de um único elemento (ver nota de implementação no resumo-tasks).
- Isolamento entre perfis deve valer também para vagas e candidaturas — complexidade: medium.
</requirements>

## Subtarefas

- [x] 3.1 Adicionar as três novas tabelas ao script de schema de `RepositorioSqlite`.
- [x] 3.2 Implementar `RepositorioVagaPort.salvar` e `listar_nao_convertidas`.
- [x] 3.3 Implementar `RepositorioCandidaturaPort.salvar`, `listar_por_perfil` e `atualizar_status`.
- [x] 3.4 Escrever testes de integração cobrindo persistência e isolamento entre perfis, seguindo o padrão de `tests/infrastructure/persistence/test_repositorio_sqlite.py` (Fase 0).

## Detalhes de Implementação

Consultar a seção "Modelos de Dados" de `techspec-job-0006.md` para o schema SQL. Reaproveitar o mesmo arquivo de teste com banco SQLite temporário (`tempfile`) já usado na Fase 0.

## Critérios de Sucesso

- Vagas e candidaturas persistem corretamente e ficam isoladas por perfil.
- `atualizar_status` reflete a mudança tanto no campo `status` quanto na data da última mudança.

## Testes da Tarefa

- [x] Teste de integração: salvar vaga, listar não convertidas, confirmar isolamento entre perfis.
- [x] Teste de integração: salvar candidatura, listar por perfil, atualizar status e confirmar a mudança persistida.
- [x] Teste de integração: candidatura de um perfil não aparece na listagem de outro perfil.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `infrastructure/persistence/repositorio_sqlite.py`
- `tests/infrastructure/persistence/test_repositorio_sqlite.py`

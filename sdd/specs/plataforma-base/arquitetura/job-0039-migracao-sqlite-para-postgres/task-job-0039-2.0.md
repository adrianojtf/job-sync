# Tarefa 2.0: Repositórios simples: perfil, token de captura e vaga

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Converte os três repositórios mais simples para o pool PostgreSQL, sem alterar as portas.

<requirements>
- Construtor recebe `pool: ConnectionPool` no lugar de `caminho_banco`.
- Placeholders `?` viram `%s`; datas passam como `datetime` (sem `isoformat`/`fromisoformat`).
- `vaga.convertida_em_candidatura` usa `BOOLEAN` (`FALSE`/`TRUE`).
- `ORDER BY` com empate por `id` usa `COLLATE "C"` quando existir.
- Os testes existentes mantêm os cenários e usam a fixture de pool.
</requirements>

## Subtarefas

- [ ] 2.1 Adaptar os testes de `perfil`, `token_captura` e `vaga` para a fixture de pool (red).
- [ ] 2.2 Converter `PerfilRepositoryImpl`.
- [ ] 2.3 Converter `TokenCapturaRepositoryImpl`.
- [ ] 2.4 Converter `VagaRepositoryImpl` (boolean e datas).
- [ ] 2.5 Conferir os fakes: nenhum deve mudar.

## Detalhes de Implementação

Techspec: "Interfaces Principais" e "Modelos de Dados" (ajustes de SQL). PRD: RF-01, RF-02.

## Critérios de Sucesso

- Todos os cenários dos três repositórios passam no Postgres.
- As portas e os fakes permanecem idênticos.

## Testes da Tarefa

- [ ] `test_perfil_repository_impl`, `test_token_captura_repository_impl`, `test_vaga_repository_impl` sobre Postgres real.
- [ ] Regressão: testes dos fakes e dos services dos três domínios.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/perfil/adapters/perfil_repository_impl.py`
- `src/jobsync/token_captura/adapters/token_captura_repository_impl.py`
- `src/jobsync/vaga/adapters/vaga_repository_impl.py`
- `src/jobsync/tests/perfil/`, `src/jobsync/tests/token_captura/`, `src/jobsync/tests/vaga/`

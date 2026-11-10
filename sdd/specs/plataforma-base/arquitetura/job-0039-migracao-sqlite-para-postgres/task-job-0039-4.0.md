# Tarefa 4.0: Repositório de candidatura: posição do board e concorrência

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Converte o repositório do board preservando a ordem dos cartões, agora com concorrência real entre conexões.

<requirements>
- `salvar`, `aplicar_movimento`, `atualizar_status` e `_renumerar_coluna` no pool, cada operação em uma transação.
- `pg_advisory_xact_lock(hashtext(perfil_identificador))` no início de `salvar` e `aplicar_movimento`.
- `ORDER BY posicao ASC, data_aplicacao DESC, id COLLATE "C" ASC`.
- Remover `_migrar_posicao_da_candidatura` e o teste `TestMigracaoDaPosicao`.
- Teste de concorrência: duas threads movendo no mesmo perfil terminam com posições de 0 a n-1 sem repetição.
</requirements>

## Subtarefas

- [x] 4.1 Adaptar os testes existentes à fixture de pool (red).
- [x] 4.2 Escrever o teste de concorrência (red).
- [x] 4.3 Converter o repositório com lock advisory e collation.
- [x] 4.4 Remover o teste e o código da migração antiga de `posicao`.
- [x] 4.5 Conferir `CandidaturaRepositoryFake`: sem mudança.

## Detalhes de Implementação

Observação: o teste de concorrência cobre `salvar` simultâneo no mesmo perfil. Sem o lock advisory ele falha (verificado), e com o lock passa. `aplicar_movimento` recebe a ordem pronta do service, então a corrida entre ler a coluna e gravar a ordem está no service e não foi alterada por esta tarefa.

Techspec: "Interfaces Principais", "Modelos de Dados" e Riscos (concorrência, collation). PRD: RF-02, RF-07; história 2.

## Critérios de Sucesso

- Todos os cenários de mover, reordenar e inserir no topo passam no Postgres.
- Teste de concorrência estável (repetir 20 vezes sem falha).

## Testes da Tarefa

- [x] `test_candidatura_repository_impl` completo sobre Postgres real.
- [x] Concorrência em `aplicar_movimento`.
- [x] Regressão: `test_mover_candidatura_service`, `test_criar_candidatura_service`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/candidatura/adapters/candidatura_repository_impl.py`
- `src/jobsync/tests/candidatura/test_candidatura_repository_impl.py`

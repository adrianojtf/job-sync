# Tarefa 5.0: Migração, domínio e repositório de `curriculo_adaptado`

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cria o contexto `curriculo_adaptado`: agregado, porta de repositório, implementação Postgres, fake e migração.

<requirements>
- Migração `0004_curriculo_adaptado.sql` com a tabela e o índice da techspec; `curriculo_salvo_id` sem chave estrangeira (decisão da migração 0002).
- Agregado `CurriculoAdaptado` imutável, com `com_rascunho_revisado(rascunho, agora)` e validações no `__post_init__`.
- Porta `CurriculoAdaptadoRepository` com `salvar`, `buscar`, `listar_por_perfil` e `vincular_curriculo_salvo`.
- Todas as consultas filtram por `perfil_identificador`.
- Serialização do rascunho e da análise da vaga em JSONB, com campo de versão do formato.
- Segue a estrutura e as convenções de `curriculo_salvo`.
</requirements>

## Subtarefas

- [x] 5.1 Testes do agregado (red).
- [x] 5.2 Testes do repositório Postgres real, seguindo `test_*_repository_impl.py` (red): salvar, buscar, listar ordenado por atualização, isolamento por perfil, vincular, ida e volta do JSONB.
- [x] 5.3 Criar o domínio e a porta (green).
- [x] 5.4 Criar a migração, o repositório e o fake (green).
- [x] 5.5 Registrar a migração no executor, se necessário.

## Detalhes de Implementação

Techspec: "Interfaces Principais", "Modelos de Dados" e "Pontos de Integração". Consumir o `curriculo` pela API pública do pacote.

## Critérios de Sucesso

- Um currículo adaptado salvo é lido de volta com o mesmo conteúdo.
- Um perfil nunca lê o currículo de outro.
- A migração aplica em banco vazio e em banco já migrado até a 0003.

## Testes da Tarefa

- [x] Testes de unidade do agregado e do fake.
- [x] Testes do repositório sobre Postgres real (contrato único para o fake e o Postgres).
- [x] Regressão: `src/jobsync/tests/shared_kernel/` (executor de migrações).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo_adaptado/` (novo)
- `src/jobsync/shared_kernel/adapters/persistence/migracoes/0004_curriculo_adaptado.sql` (novo)
- `src/jobsync/curriculo_salvo/` (modelo)
- `src/jobsync/tests/curriculo_adaptado/` (novo)

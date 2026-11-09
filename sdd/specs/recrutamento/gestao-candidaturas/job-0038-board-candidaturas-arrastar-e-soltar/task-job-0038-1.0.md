# Tarefa 1.0: Domínio e persistência da ordem dos cartões

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cada candidatura passa a ter uma posição dentro da coluna (perfil + status). Esta tarefa cria o campo, a regra pura de reordenação, a migração do SQLite e a leitura ordenada. Não mexe em API nem em frontend.

<requirements>
- Adicionar `posicao: int` (>= 0) a `Candidatura`; `Candidatura.nova` usa `posicao=0`; valor negativo levanta `ValueError`.
- Criar `candidatura/domain/ordenacao_coluna.py` com `reposicionar(ids, movido_id, posicao)`: `None` = topo, posição acima do tamanho = fim, e o movido já presente é removido antes de inserir.
- Estender a porta `CandidaturaRepository` com `buscar_por_id` e `aplicar_movimento(candidatura_id, novo_status, ids_destino_ordenados)`.
- Em `CandidaturaRepositoryImpl`: coluna `posicao`, `listar_por_perfil` com `ORDER BY posicao`, `salvar` insere no topo do status (renumera a coluna) e `aplicar_movimento` fecha o vazio da origem e grava a ordem do destino em uma transação.
- Migração idempotente em `criar_conexao`: se `PRAGMA table_info(candidatura)` não tiver `posicao`, executar `ALTER TABLE` e numerar cada `(perfil, status)` por `data_aplicacao DESC`.
</requirements>

## Subtarefas

- [x] 1.1 Escrever os testes de `reposicionar` e da validação de `posicao` (red).
- [x] 1.2 Implementar `ordenacao_coluna.py` e o campo em `Candidatura`.
- [x] 1.3 Escrever os testes do repositório SQLite (ordem, `salvar` no topo, `aplicar_movimento`, migração de banco antigo).
- [x] 1.4 Estender a porta e implementar `buscar_por_id`, `aplicar_movimento` e a migração.
- [x] 1.5 Ajustar os fakes e testes existentes que constroem `Candidatura` ou implementam a porta.

## Detalhes de Implementação

Techspec: "Visão Geral dos Componentes" (backend), "Interfaces Principais" e "Modelos de Dados". PRD: RF8, RF10, RF11.

## Critérios de Sucesso

- A ordem sobrevive a nova abertura do banco.
- Banco criado antes desta tarefa abre sem perda de dados e com a ordem por data de aplicação.
- Nenhuma transação deixa a coluna com posições duplicadas ou buracos.

## Testes da Tarefa

- [x] `reposicionar`: início, meio, fim, acima do tamanho, `None`, movido já presente, coluna vazia.
- [x] `Candidatura` rejeita `posicao` negativa.
- [x] Repositório: ordem por `posicao`; `salvar` entra no topo; `aplicar_movimento` fecha o vazio e não deixa estado parcial; migração idempotente (rodar duas vezes).
- [x] Regressão: `test_candidatura.py`, `test_candidatura_repository*.py` e demais testes de `candidatura/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/candidatura/domain/candidatura.py`
- src/jobsync/candidatura/domain/ordenacao_coluna.py (novo)
- `src/jobsync/candidatura/domain/candidatura_repository.py`
- `src/jobsync/candidatura/adapters/candidatura_repository_impl.py`
- `src/jobsync/shared_kernel/adapters/persistence/_conexao_sqlite.py`
- `src/jobsync/tests/candidatura/`

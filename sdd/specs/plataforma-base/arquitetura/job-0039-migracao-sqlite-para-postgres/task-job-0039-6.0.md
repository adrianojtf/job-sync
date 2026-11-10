# Tarefa 6.0: Núcleo da migração de dados SQLite para PostgreSQL

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementa a lógica que lê o SQLite, valida a origem, copia para o Postgres em uma transação e confere o resultado.

<requirements>
- Abrir o SQLite com URI `file:...?mode=ro` (RF-13).
- Pré-checagens (RF-11): coluna `candidatura.posicao` presente, `PRAGMA foreign_key_check` vazio, datas e `*_json` interpretáveis; reunir todos os problemas antes de abortar.
- Exigir destino com as seis tabelas vazias (RF-10).
- Copiar na ordem `perfil`, `curriculo_salvo`, `token_captura`, `vaga`, `candidatura`, `perfil_estruturado`, em lotes, convertendo data, booleano e JSON (RF-06, RF-07).
- Validar na mesma transação: contagem por tabela, SHA-256 de cada `pdf_bytes` e sequência de `posicao` por `(perfil, status)` (RF-12).
- Tudo ou nada (RF-09); dry-run executa tudo e reverte inclusive o DDL (RF-08).
</requirements>

## Subtarefas

- [x] 6.1 Escrever testes das conversões puras (data, booleano, JSON, hash) (red).
- [x] 6.2 Implementar as conversões e o modelo de relatório.
- [x] 6.3 Escrever testes de integração com SQLite temporário: caminho feliz, órfão, data inválida, JSON inválido, `posicao` ausente (red).
- [x] 6.4 Implementar leitura somente leitura e pré-checagens.
- [x] 6.5 Implementar cópia transacional, validação e dry-run.
- [x] 6.6 Testar rollback por falha induzida, destino com dados, segunda execução e `.db` inalterado (hash antes e depois).

## Detalhes de Implementação

Techspec: "CLI de migração de dados" e "Testes da CLI de migração". PRD: RF-06 a RF-13.

## Critérios de Sucesso

- Contagens, hashes de PDF e posições iguais na origem e no destino.
- Falha em qualquer etapa deixa o destino vazio.
- O arquivo `.db` não é modificado.

## Testes da Tarefa

- [x] Conversões puras sem banco.
- [x] Cenários completos da Tech Spec com SQLite temporário criado via `sqlite3` e Postgres real.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/shared_kernel/adapters/persistence/migracao_sqlite.py` (novo)
- `src/jobsync/tests/shared_kernel/` (novos testes)

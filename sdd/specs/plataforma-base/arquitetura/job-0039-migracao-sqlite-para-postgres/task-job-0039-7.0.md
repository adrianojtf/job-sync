# Tarefa 7.0: CLI de migração de dados

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expõe a migração como comando de terminal, com relatório claro em português e códigos de saída por tipo de falha.

<requirements>
- `python -m jobsync.entrypoints.cli.migrar_sqlite_para_postgres --sqlite <caminho> [--dry-run]`; destino lido de `DATABASE_URL`.
- Códigos de saída: 0 sucesso, 2 problemas na origem, 3 destino inválido ou não vazio, 4 divergência na validação.
- Relatório final no `stdout` com tabela, lidos, gravados e validação; sem credenciais.
- Mensagens em português com o próximo passo em cada falha.
- Criar o pacote `entrypoints/cli/` e conferir `test_arquitetura.py`.
</requirements>

## Subtarefas

- [ ] 7.1 Escrever testes da CLI com `subprocess`/`main(argv)`: códigos de saída e conteúdo do relatório (red).
- [ ] 7.2 Implementar argumentos, relatório e códigos de saída.
- [ ] 7.3 Garantir que a senha nunca aparece em `stdout` nem em logs.
- [ ] 7.4 Rodar `lint-imports` e ajustar contratos se necessário.

## Detalhes de Implementação

Techspec: "CLI de migração de dados" e "Monitoramento e Observabilidade". PRD: RF-08, RF-12; histórias 4 e 5.

## Critérios de Sucesso

- Cada código de saída é coberto por teste.
- O relatório permite a um operador confirmar que nada se perdeu.

## Testes da Tarefa

- [ ] Testes de ponta a ponta da CLI com origem SQLite temporária e Postgres real.
- [ ] Senha ausente da saída.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/cli/__init__.py`, `src/jobsync/entrypoints/cli/migrar_sqlite_para_postgres.py` (novos)
- `src/jobsync/tests/entrypoints/cli/` (novo)
- `setup.cfg` (se necessário)

# Tarefa 3.0: Implementar RepositorioSqlite com testes de integração

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o adapter de infraestrutura que dá vida às duas portas definidas na Tarefa 2.0, usando `sqlite3` da biblioteca padrão do Python, com o arquivo de banco em `storage/job_sync.db`.

<requirements>
- Criar as tabelas `perfil` e `curriculo_salvo` conforme o schema definido na Tech Spec, incluindo a criação automática do schema se o banco ainda não existir.
- `RepositorioSqlite` deve implementar `RepositorioPerfilPort` e `RepositorioCurriculoSalvoPort` na mesma classe (reaproveitando a conexão).
- Garantir isolamento entre perfis: `listar_por_perfil` de um perfil nunca deve retornar currículos de outro — complexidade: medium.
</requirements>

## Subtarefas

- [x] 3.1 Definir o schema SQL (`CREATE TABLE IF NOT EXISTS`) para `perfil` e `curriculo_salvo`, executado na inicialização do repositório.
- [x] 3.2 Implementar os métodos de `RepositorioPerfilPort` (`buscar_por_identificador`, `criar`).
- [x] 3.3 Implementar os métodos de `RepositorioCurriculoSalvoPort` (`salvar`, `listar_por_perfil`, `remover`, `contar_por_perfil`).
- [x] 3.4 Escrever testes de integração usando um arquivo SQLite temporário (`tempfile`), cobrindo o isolamento entre perfis diferentes.

## Detalhes de Implementação

Consultar as seções "Modelos de Dados" (schema SQL) e "Abordagem de Testes > Testes de Serviço" de `techspec-job-0004.md`. Nenhuma biblioteca nova é necessária (`sqlite3` é stdlib).

## Critérios de Sucesso

- Perfis e currículos salvos persistem entre reinicializações do processo (arquivo `storage/job_sync.db`).
- Um perfil nunca acessa currículos de outro perfil.
- `contar_por_perfil` reflete corretamente a quantidade de currículos salvos ativos.

## Testes da Tarefa

- [x] Teste de integração: criar perfil, buscar por identificador, confirmar persistência.
- [x] Teste de integração: salvar currículo, listar por perfil, remover, confirmar contagem atualizada.
- [x] Teste de integração: perfil A não vê currículos salvos do perfil B.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `infrastructure/persistence/repositorio_sqlite.py`
- `tests/infrastructure/persistence/test_repositorio_sqlite.py`
- `storage/` (diretório onde `job_sync.db` passa a ser criado)

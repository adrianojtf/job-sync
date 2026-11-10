# Tech Spec — Migração do banco de SQLite para PostgreSQL

- **Código**: `job-0039`
- **Módulo**: `plataforma-base`
- **Subsistema**: `arquitetura`
- **Status**: Rascunho
- **Baseado em**: [prd-job-0039.md](prd-job-0039.md)

## Resumo Executivo

Os seis `*RepositoryImpl` hoje abrem uma conexão SQLite própria por instância e rodam o schema (`CREATE TABLE IF NOT EXISTS`) a cada abertura, via `shared_kernel/adapters/persistence/_conexao_sqlite.py`. A solução troca esse módulo por um pool de conexões PostgreSQL (`psycopg` 3 + `psycopg_pool`), criado uma vez na raiz de composição e injetado nos repositórios. O schema passa a ser aplicado por migrações SQL versionadas, executadas uma vez na subida da API. As portas (`domain/*_repository.py`) e os fakes não mudam, então services, routers e frontend ficam intactos.

Os dados atuais migram por uma CLI única, `python -m jobsync.entrypoints.cli.migrar_sqlite_para_postgres`. Ela lê o `.db` em modo somente leitura, valida a origem, grava tudo em uma transação no PostgreSQL, confere contagens e hashes e só então faz commit. O SQLite sai do runtime e permanece apenas como fonte de leitura da CLI. O arquivo `.db` é o ponto de retorno.

Analogia: a CLI é uma mudança com inventário. Cada caixa é listada na origem, conferida no destino, e a mudança só vale se o inventário fecha.

## Arquitetura do Sistema

### Visão Geral dos Componentes

| Componente | Situação | Responsabilidade |
| --- | --- | --- |
| `shared_kernel/adapters/persistence/_conexao_sqlite.py` | Removido | Substituído pelos três módulos abaixo. A lógica `_migrar_posicao_da_candidatura` sai do runtime. |
| `shared_kernel/adapters/persistence/conexao_postgres.py` | Novo | Cria o `ConnectionPool` a partir de `DATABASE_URL`, falha rápido se não conectar e mascara a senha nos logs. |
| `shared_kernel/domain/relogio.py` | Novo | `agora_utc()`, usado pelos services e pelo repositório de candidatura. |
| `shared_kernel/adapters/persistence/migracoes/` | Novo | Arquivos `NNNN_descricao.sql` e `executor_migracoes.py`, que aplica os pendentes e registra em `schema_migrations`. |
| `shared_kernel/adapters/persistence/migracao_sqlite.py` | Novo | Lógica da migração de dados: leitura, conversão, validação e gravação. |
| `entrypoints/cli/migrar_sqlite_para_postgres.py` | Novo | Interface de linha de comando (argumentos, relatório, códigos de saída). |
| `perfil`, `token_captura`, `vaga`, `candidatura`, `curriculo_salvo`, `perfil_estruturado` — `*_repository_impl.py` | Alterados | Recebem o pool no construtor, trocam `?` por `%s` e removem a conversão manual de tipos. |
| `entrypoints/dependencies.py` | Alterado | `obter_caminho_banco` vira `obter_pool_conexoes` (singleton). Os `obter_repositorio_*` passam o pool. Remove `JOB_SYNC_DB_PATH`. |
| `entrypoints/api/dependencies.py` | Alterado | Remove `CaminhoBancoDep`, que não tem nenhum uso. |
| `entrypoints/api/main.py` | Alterado | `lifespan` aplica migrações na subida e fecha o pool no desligamento. |
| `requirements.txt`, `requirements-backend.txt` | Alterados | Adicionam `psycopg[binary]` e `psycopg-pool`. |
| `.env.example`, `docker-compose.yml`, `Dockerfile`, `README.md`, `.github/workflows/ci.yml`, `frontend/playwright.config.ts`, `tests/e2e/app_e2e.py` | Alterados | `DATABASE_PATH` vira `DATABASE_URL`. Ver "Sequenciamento". |

Fluxo em produção: `lifespan` cria o pool, aplica as migrações e guarda o pool. Cada request resolve `obter_repositorio_*`, que usa o pool compartilhado. Cada operação pega uma conexão do pool, abre transação e devolve a conexão.

## Design de Implementação

### Interfaces Principais

As portas não mudam. Os construtores dos adapters mudam de `caminho_banco: str` para o pool:

```python
class CandidaturaRepositoryImpl(CandidaturaRepository):
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        with self._pool.connection() as conexao:  # commit ao sair, rollback em exceção
            conexao.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (candidatura.perfil_identificador,))
            ...
```

```python
def executar_migracoes(conexao: Connection) -> list[str]:
    """Aplica migrações pendentes dentro da transação do chamador; devolve as versões aplicadas."""
```

Decisão sobre o uso: o `executor_migracoes` não faz commit. Quem o chama controla a transação: o `lifespan` confirma, e a CLI em dry-run reverte. O DDL do PostgreSQL é transacional, então o dry-run desfaz inclusive a criação das tabelas.

Mantém-se uma classe de repositório por porta, como justifica a docstring do módulo antigo: `salvar` e `listar_por_perfil` existem em várias portas com tipos diferentes.

### Modelos de Dados

Migração `0001_schema_inicial.sql`, equivalente ao schema atual:

| SQLite | PostgreSQL | Observação |
| --- | --- | --- |
| `id`, `identificador`, `token` `TEXT` | `TEXT` | Mantém os UUIDs como texto (YAGNI). |
| `data_*` `TEXT` ISO-8601 | `TIMESTAMPTZ` (UTC) | O domínio passa a usar `agora_utc()` (`shared_kernel/domain/relogio.py`). A API devolve a data com fuso (`...Z`) e o navegador a exibe no fuso do usuário, com `new Date(iso)` e `Intl`, que o frontend já usa. Nenhum header de fuso é necessário. |
| `pdf_bytes BLOB` | `BYTEA` | |
| `convertida_em_candidatura INTEGER 0/1` | `BOOLEAN NOT NULL DEFAULT FALSE` | |
| `*_json TEXT` | `JSONB NOT NULL DEFAULT '[]'` | Remove `json.dumps` e `json.loads`. |
| `posicao INTEGER NOT NULL DEFAULT 0` | igual | A coluna já nasce no `0001`. |

As chaves estrangeiras continuam as mesmas e passam a ser sempre validadas pelo PostgreSQL. No SQLite elas só valem com `PRAGMA foreign_keys=ON`, que o código atual não liga. Por isso podem existir órfãos no `.db` (tratado na CLI). Não são criados índices novos, conforme o PRD.

Ajustes de SQL nos repositórios:

- Placeholders `?` viram `%s`.
- Datas passam como `datetime`, sem `isoformat()` nem `fromisoformat()`.
- JSON passa por `psycopg.types.json.Jsonb(...)` na escrita. Na leitura, o driver já devolve `list`.
- Empates de ordenação usam `ORDER BY ..., id COLLATE "C"`, para reproduzir a ordem binária do SQLite.
- `aplicar_movimento` e `salvar` de candidatura tomam `pg_advisory_xact_lock(hashtext(perfil))` no início da transação.

### Endpoints de API

Sem mudança de contrato (regra `back-end-general-rules.md`: só alterar contrato quando solicitado). O OpenAPI e `frontend/src/api/schema.d.ts` permanecem iguais, e o job de CI "Contrato da API" confirma isso.

### CLI de migração de dados

```
python -m jobsync.entrypoints.cli.migrar_sqlite_para_postgres \
  --sqlite storage/job_sync.db --destino-env DATABASE_URL [--dry-run]
```

Fluxo (ordem pela dependência de FK: `perfil`, `curriculo_salvo`, `token_captura`, `vaga`, `candidatura`, `perfil_estruturado`):

1. Abre o SQLite com URI `file:...?mode=ro`.
2. Pré-checagens na origem. Qualquer problema aborta com código de saída 2 e lista tudo de uma vez:
   - `candidatura.posicao` existe. Se não existir, a mensagem manda subir uma vez a versão anterior do sistema, que já aplica essa migração.
   - `PRAGMA foreign_key_check` vazio.
   - Todas as datas e todos os `*_json` são interpretáveis.
3. No destino, abre uma transação, chama `executar_migracoes` e confirma que as seis tabelas estão vazias (RF-10). Se não estiverem, aborta com código 3.
4. Copia em lotes com `executemany`, convertendo data para `datetime`, inteiro para `bool` e texto JSON para `Jsonb`.
5. Valida ainda dentro da transação: contagem por tabela, SHA-256 de cada `pdf_bytes` e igualdade da sequência de `posicao` por `(perfil, status)`. Qualquer divergência causa rollback e código de saída 4.
6. Sem `--dry-run`, faz commit. Com `--dry-run`, faz rollback e informa o que teria sido gravado.
7. Imprime o relatório (tabela, lidos, gravados, validação), sem credenciais.

## Pontos de Integração

- **PostgreSQL local**: versão 15.3, instalado na máquina, fora do compose. Requisitos: banco e usuário dedicados, `DATABASE_URL=postgresql://usuario:senha@host:5432/job_sync`.
- **Backend em container (fase posterior)**: por enquanto o backend roda direto na máquina e usa `localhost` na `DATABASE_URL`. Quando for para container, o `docker-compose.yml` ganha `extra_hosts: ["host.docker.internal:host-gateway"]`. O `postgresql.conf` precisa escutar na interface da bridge do Docker e o `pg_hba.conf` precisa liberar a rede do container. Isso é configuração da máquina e entra no README.
- **Falhas**: sem `DATABASE_URL` ou sem conexão, a API não sobe e registra o erro sem a senha (RF-04).

## Abordagem de Testes

Segue `testing-rules.md`, com TDD (Red-Green-Refactor) por tarefa.

### Testes Unidade

- Funções puras de conversão da CLI (data, booleano, JSON, hash de PDF) e o formatador de relatório. Sem banco e sem mocks.
- Mascaramento de senha da URL.

### Testes de Integração (PostgreSQL real)

- Fixture em `tests/conftest.py`: lê `TEST_DATABASE_URL`, aplica as migrações uma vez por sessão e executa `TRUNCATE ... RESTART IDENTITY CASCADE` entre testes. Sem a variável, os testes de repositório fazem `skip` com mensagem explícita. O CI sempre define a variável.
- Os testes existentes de `*_repository_impl` trocam `caminho_banco` pela fixture de pool, mantendo os cenários.
- `TestMigracaoDaPosicao` (SQLite) é removido. Seu cenário vira teste da CLI: origem sem `posicao` é recusada com mensagem orientativa.
- Novo teste de concorrência: duas threads chamam `aplicar_movimento` no mesmo perfil, e as posições finais continuam sequenciais de 0 a n-1, sem duplicidade.
- `test_candidaturas_ajustadas_router.py` troca a consulta `PRAGMA foreign_key_check` por contagens SQL. O PostgreSQL já impede violação de FK.
- `test_seguranca_dependencias.py` passa a configurar `DATABASE_URL`.

### Testes da CLI de migração

O arquivo SQLite de teste é criado com `sqlite3` da biblioteca padrão dentro do teste. Cenários:

- Caminho feliz com PDF binário, board com ordem definida e JSONs.
- Órfão de FK, data inválida e JSON inválido são relatados e abortam sem gravar.
- Destino com dados é recusado.
- Segunda execução não duplica.
- `--dry-run` deixa o destino sem tabelas e sem linhas.
- Falha induzida no meio da cópia deixa o destino vazio (rollback).
- O arquivo `.db` não é modificado (hash antes e depois).

### Testes E2E

`frontend/playwright.config.ts` e `app_e2e.py` passam a usar `DATABASE_URL` (banco `job_sync_e2e`), recriando as tabelas vazias antes da execução.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Dependências, `conexao_postgres.py` e `executor_migracoes` com `0001` (base de todo o resto).
2. Fixture de teste e CI com serviço `postgres:16` nos jobs `lint-and-test` e `e2e`.
3. Repositórios, um por tarefa, do mais simples ao mais complexo: `perfil`, `token_captura`, `vaga`, `curriculo_salvo`, `perfil_estruturado`, `candidatura`.
4. Raiz de composição, `lifespan` e remoção de `_conexao_sqlite.py`.
5. CLI de migração de dados, com testes.
6. Docker, `.env.example`, README (instalação do Postgres, `DATABASE_URL`, roteiro de troca e de retorno), E2E.
7. Ensaio com cópia real do `job_sync.db` em `--dry-run`, depois a troca real.

Roteiro de troca (RF-14): parar a API, copiar o `.db` para backup, rodar a CLI com `--dry-run`, rodar sem `--dry-run`, subir a API com `DATABASE_URL`, conferir o board. Retorno (RF-15): voltar à versão anterior do sistema com `DATABASE_PATH`. Os dados gravados no PostgreSQL depois da troca não voltam sozinhos.

### Dependências Técnicas

- PostgreSQL instalado e acessível, com banco e usuário criados.
- Versões exatas de `psycopg` e `psycopg-pool` a fixar na implementação (série 3.2, a validar com Python 3.12).
- Serviço PostgreSQL disponível no GitHub Actions.
- Recursos usados (`pg_advisory_xact_lock`, `JSONB`, `ON CONFLICT`) existem no PostgreSQL 15.3, e o CI usa `postgres:16`. Rodar a suíte também contra a versão 15 é uma melhoria opcional.

## Monitoramento e Observabilidade

- `INFO` na subida: host, porta e nome do banco (sem usuário e senha), tamanho do pool e migrações aplicadas.
- `ERROR` com causa resumida quando a conexão falha. A senha nunca é registrada.
- A CLI usa `logging` e imprime o relatório final no `stdout`, com código de saída por tipo de falha (2 origem, 3 destino, 4 validação).
- Operações do board continuam com os logs atuais. Não há novas métricas (YAGNI).

## Considerações Técnicas

### Decisões Principais

- **`psycopg` 3 com SQL puro, sem ORM.** Mantém o desenho atual (adapters finos e SQL explícito) e evita reescrever a persistência. Alternativa rejeitada: SQLAlchemy, que muda o estilo de todos os adapters sem necessidade.
- **Migrações em SQL com executor próprio.** São cerca de 40 linhas, e o schema tem seis tabelas. Alternativa rejeitada: Alembic, que traz SQLAlchemy só para isso. Reavaliar se o número de migrações crescer.
- **Pool compartilhado, em vez de uma conexão por repositório.** Hoje cada request abre várias conexões SQLite e reexecuta o schema. Com PostgreSQL isso esgotaria conexões do servidor.
- **Migração em transação única com dry-run por rollback.** Garante tudo ou nada com pouco código. Alternativa rejeitada: dual-write, por complexidade desproporcional para um sistema de uso individual.
- **Fuso: instantes em UTC com fuso (`TIMESTAMPTZ`).** Decisão do responsável: usar o fuso do usuário recebido pelo navegador. Como o navegador já converte datas ISO com offset, o servidor só precisa devolver instantes sem ambiguidade. Alternativa rejeitada: header `X-Timezone` e conversão no servidor, que adicionaria código sem benefício para os valores armazenados.
- **Sem chave estrangeira em `candidatura.curriculo_salvo_id` (migração `0002`).** O sistema sempre permitiu remover um currículo salvo em uso, pois o SQLite não validava a chave, e a tela já trata currículo ausente. Com a chave validada no Postgres, essa remoção passaria a dar erro 500. A chave foi removida para preservar o comportamento, e a CLI migra essas candidaturas com aviso. Alternativa rejeitada: bloquear a remoção, que é regra de negócio nova.
- **Sem SQLite no runtime.** Evita manter dois adapters. Os fakes cobrem os testes de service, e os testes de repositório usam PostgreSQL real.

### Riscos Conhecidos

| Risco | Mitigação |
| --- | --- |
| Órfãos de FK no `.db` (as FKs não eram validadas) | Pré-checagem lista tudo e aborta. Exceção: candidatura com currículo salvo removido é migrada com aviso (migração `0002`). Correção manual dos demais antes de repetir. |
| Concorrência no reordenamento do board (antes serializada pelo SQLite) | Lock advisory por perfil e teste de concorrência. |
| Datas antigas sem fuso (`datetime.now()` da máquina) | A CLI as interpreta no fuso local da máquina, ou em `--fuso-origem`, e grava em UTC. Se a máquina que criou o banco usava outro fuso, informe `--fuso-origem`. |
| Ordem de desempate por `id` diferente por collation | `COLLATE "C"` nos `ORDER BY`. Após a migração `posicao` é única por coluna, então o impacto é baixo. |
| Container não alcança o Postgres do host | Documentar `extra_hosts`, `listen_addresses` e `pg_hba.conf`. Teste manual no roteiro de troca. |
| Tipos retornados pelo driver (`bytea`, `jsonb`) | Testes de integração cobrem PDF e JSON em ida e volta. Esta especificação assume que o driver devolve `bytes` e `list`, e os testes confirmam. |
| Perda de dados gravados após a troca ao voltar para o SQLite | Documentado no roteiro de retorno. |

### Conformidade com Padrões

- `.windsurf/rules/general-rules.md` e `AGENTS.md`: Hexagonal e ports and adapters (portas intactas), KISS/YAGNI (sem ORM, sem dual-write), TDD, mudanças restritas ao pedido.
- `.windsurf/rules/code-design-standards.md`: persistência fica em `adapters/`. A CLI fica em `entrypoints/`, e a lógica compartilhada em `shared_kernel/adapters`.
- `.windsurf/rules/back-end-general-rules.md`: contrato de API inalterado.
- `.windsurf/rules/testing-rules.md`: classes `Test<Classe>`, blocos Arrange/Act/Assert separados e sem comentários nos testes.
- `import-linter` (`setup.cfg`): `sqlite3` é biblioteca padrão e fica só em `shared_kernel/adapters` e nos testes. Nenhum contrato de camada é afetado.

Desvios: nenhum identificado. A confirmar na implementação: se o novo pacote `entrypoints/cli/` exige ajuste no `test_arquitetura.py`.

### Arquivos relevantes e dependentes

- `src/jobsync/shared_kernel/adapters/persistence/_conexao_sqlite.py` (remover)
- `src/jobsync/{perfil,token_captura,vaga,candidatura,curriculo_salvo,perfil_estruturado}/adapters/*_repository_impl.py`
- `src/jobsync/entrypoints/dependencies.py`, `src/jobsync/entrypoints/api/dependencies.py`, `src/jobsync/entrypoints/api/main.py`
- Testes: `tests/{perfil,token_captura,vaga,candidatura,curriculo_salvo,perfil_estruturado}/test_*_repository_impl.py`, `tests/entrypoints/api/test_candidaturas_ajustadas_router.py`, `tests/entrypoints/api/test_seguranca_dependencias.py`, `tests/e2e/app_e2e.py`, `tests/test_arquitetura.py`
- `frontend/playwright.config.ts`, `.github/workflows/ci.yml`, `docker-compose.yml`, `Dockerfile`, `.env.example`, `requirements.txt`, `requirements-backend.txt`, `README.md`

## Questões em Aberto

1. Resolvida: datas em `TIMESTAMPTZ` (UTC), exibidas no fuso do navegador. Já o `date.today()` de `NomeArquivo` e de `DescobrirVagasComMatch` continua usando a data do servidor. Se a data do nome do PDF precisar seguir o fuso do usuário, o frontend deve enviar `data_referencia`.
2. Resolvida: o sistema não está em produção, então a janela de parada não é restrição agora. Rever antes de ir para produção.

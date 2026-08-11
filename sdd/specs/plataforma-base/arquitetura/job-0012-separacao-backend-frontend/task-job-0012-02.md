# Tarefa 02: Adaptar/expor repositórios existentes

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Garantir que os repositórios e adapters de infraestrutura existentes do `jobsync` possam ser injetados nos endpoints do backend sem duplicar implementação.

<requirements>
- Auditar repositórios `Impl` em `<dominio>/adapters/` e garantir que implementam as interfaces de `domain`.
- Revisar conexão SQLite e path configurável via variável de ambiente.
- Manter interfaces em `<dominio>/domain/<entidade>_repository.py` sem dependência de infraestrutura.
- Criar fakes/stubs em `<dominio>/adapters/<entidade>_repository_fake.py` para testes de API.
- Garantir que cada repositório retorne agregados completos.
</requirements>

## Subtarefas

- [ ] 2.1 Mapear todos os repositórios `Impl` existentes por domínio.
- [ ] 2.2 Criar/adaptar fakes para testes de API.
- [ ] 2.3 Verificar se os `__init__.py` de `adapters` exportam os tipos públicos.
- [ ] 2.4 Adicionar/ajustar variável `DATABASE_PATH` no `.env.example`.

## Detalhes de Implementação

Ver `techspec-job-0012.md` -> Pontos de Integração -> SQLite. Os repositórios existentes devem ser reutilizados, não reescritos.

## Critérios de Sucesso

- Todos os repositórios `Impl` são instanciáveis via `dependencies.py`.
- Fakes retornam dados consistentes para testes de router.
- `import-linter` não detecta `domain` importando `adapters`.

## Testes da Tarefa

- [ ] `pytest` nos testes de repositórios passa.
- [ ] Testes de importação dos fakes não quebram.
- [ ] `lint-imports` passa.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/*/adapters/*_repository_impl.py`
- `src/jobsync/*/domain/*_repository.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `.env.example`

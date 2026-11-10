# Tarefa 1.0: Migração `0003_autenticacao.sql`, entidades de domínio e value objects

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar o domínio `autenticacao` (pacote `src/jobsync/autenticacao/`) com as entidades e value objects puros, sem dependência de infraestrutura, e a migração SQL que cria as tabelas. Registrar o novo domínio nos contratos do `import-linter` em `setup.cfg`. Complexidade: medium.

<requirements>
- Entidades imutáveis: `Usuario`, `IdentidadeExterna`, `Sessao`, `TokenUsoUnico`, `EstadoOAuth`.
- Value objects: `Email` (normalizado em minúsculas, formato validado) e `Senha` (política: 10 a 128 caracteres, rejeita senhas comuns e senha igual à parte local do e-mail).
- Instantes sempre em UTC, vindos do relógio do domínio (`shared_kernel/domain/relogio.py`).
- `Usuario` referencia `Perfil` apenas por `perfil_identificador` (regra de dependência entre domínios).
- Migração `0003_autenticacao.sql` conforme "Modelos de Dados" da Tech Spec.
- `jobsync.autenticacao` incluído em `containers` dos contratos de `setup.cfg`.
</requirements>

## Subtarefas

- [ ] 1.1 Escrever testes (TDD) dos value objects `Email` e `Senha`.
- [ ] 1.2 Implementar `Email` e `Senha` em `autenticacao/domain/`.
- [ ] 1.3 Escrever testes e implementar `Usuario` e `IdentidadeExterna`.
- [ ] 1.4 Escrever testes e implementar `Sessao` (expiração por inatividade e absoluta), `TokenUsoUnico` e `EstadoOAuth`.
- [ ] 1.5 Criar a migração `0003_autenticacao.sql`.
- [ ] 1.6 Registrar `jobsync.autenticacao` em `setup.cfg` e rodar `lint-imports`.

## Detalhes de Implementação

Ver "Visão Geral dos Componentes" e "Modelos de Dados" em `techspec-job-0013.md`. Seguir o estilo de `perfil/domain/perfil.py` (dataclass `frozen`, validação em `__post_init__`). Os identificadores de usuário são UUID.

## Critérios de Sucesso

- Entidades rejeitam estados inválidos (e-mail malformado, senha fora da política, expiração anterior à criação).
- A migração aplica em banco limpo e em banco com a `0001` e a `0002` já aplicadas.
- `lint-imports` passa com o novo domínio.

## Testes da Tarefa

- [ ] Testes de unidade dos value objects e entidades
- [ ] Teste de aplicação da migração (quando `TEST_DATABASE_URL` estiver definida)

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/autenticacao/domain/*.py`
- `src/jobsync/shared_kernel/adapters/persistence/migracoes/0003_autenticacao.sql`
- `setup.cfg`
- `src/jobsync/tests/autenticacao/`

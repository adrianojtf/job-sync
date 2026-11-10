# Tarefa 8.0: CLI `associar_email_perfil` para migrar perfis legados

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Dar ao mantenedor um comando que associa um e-mail a um perfil legado, criando o `Usuario` sem credencial e sem e-mail verificado. O vínculo se completa no primeiro login com esse e-mail verificado. Complexidade: low.

<requirements>
- Caso de uso `AssociarEmailAPerfil`: perfil precisa existir; e-mail não pode pertencer a outro usuário; perfil não pode ter usuário.
- CLI `python -m jobsync.entrypoints.cli.associar_email_perfil --perfil <id> --email <email>`, no estilo de `migrar_sqlite_para_postgres.py`.
- Operação idempotente quando o mesmo par já existe.
- Não altera dados do perfil.
- Log INFO sem e-mail completo.
</requirements>

## Subtarefas

- [x] 8.1 Serviço `AssociarEmailAPerfil` com testes.
- [x] 8.2 CLI com testes (padrão de `tests/entrypoints/cli`).
- [x] 8.3 Instruções de uso no README (a tarefa 10.0 consolida).

## Detalhes de Implementação

Ver "Resolução da identidade" e "Decisões Principais" em `techspec-job-0013.md`.

## Critérios de Sucesso

- Após a CLI, `ConcluirLoginOAuth` com o e-mail verificado vincula o perfil legado.
- Conflitos geram mensagem clara e código de saída diferente de zero.

## Testes da Tarefa

- [x] Testes de unidade do serviço e da CLI

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/autenticacao/service_layer/associar_email_a_perfil/service.py`
- `src/jobsync/entrypoints/cli/associar_email_perfil.py`
- `src/jobsync/tests/entrypoints/cli/`

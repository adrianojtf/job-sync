# Tarefa 8.0: Configuração e documentação

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Atualiza a configuração de execução e documenta instalação, troca e retorno.

<requirements>
- `.env.example`: `DATABASE_PATH` vira `DATABASE_URL` com exemplo e comentário.
- `docker-compose.yml` (uso em container é fase posterior; entra aqui só a preparação): remover `DATABASE_PATH`, manter o volume `storage` para PDFs e adicionar `extra_hosts: ["host.docker.internal:host-gateway"]`.
- `Dockerfile`: remover `ENV DATABASE_PATH`; sem valor padrão de `DATABASE_URL`.
- README: instalar e configurar o Postgres local 15.3 (banco, usuário, `listen_addresses`, `pg_hba.conf`), variáveis, roteiro de troca (RF-14) e roteiro de retorno (RF-15); atualizar menções a SQLite.
- Atualizar a seção de testes E2E do README.
</requirements>

## Subtarefas

- [x] 8.1 Atualizar `.env.example`, `docker-compose.yml` e `Dockerfile`.
- [x] 8.2 Escrever no README o passo a passo do Postgres local e da `DATABASE_URL`.
- [x] 8.3 Escrever o roteiro de troca e o de retorno, com o aviso sobre dados gravados após a troca.
- [x] 8.4 Revisar todas as menções a SQLite e `DATABASE_PATH` no repositório.

## Detalhes de Implementação

Techspec: "Pontos de Integração" e "Sequenciamento". PRD: RF-14, RF-15; história 7.

## Critérios de Sucesso

- Uma pessoa nova consegue subir o ambiente só com o README.
- Nenhuma menção residual a `DATABASE_PATH` fora do roteiro de retorno.

## Testes da Tarefa

- [x] `docker compose config` válido.
- [x] Conferência por busca: `grep -rn "DATABASE_PATH\|sqlite"`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `.env.example`
- `docker-compose.yml`
- `Dockerfile`
- `README.md`
- `README-macos.md`

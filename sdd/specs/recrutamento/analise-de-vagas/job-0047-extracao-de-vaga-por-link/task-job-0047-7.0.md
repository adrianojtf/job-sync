# Tarefa 7.0: Persistência de cargo, empresa e local na captura de vagas

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Permitir guardar `cargo`, `empresa` e `local` na vaga capturada, de forma aditiva e compatível com os dados e clientes existentes.

Complexidade: medium. Dependências: 1.0.

<requirements>
- Migração `0005_vaga_dados_extraidos.sql` com colunas `cargo`, `empresa` e `local`, todas nulas.
- `Vaga` ganha os três campos opcionais.
- `VagaRepositoryImpl` e `VagaRepositoryFake` gravam e leem os campos. Linhas antigas retornam nulos.
- `CapturarVagaInputDto`, validador e serviço aceitam os campos.
- `VagaCapturarRequest` e `VagaResponse` ganham os campos opcionais, sem quebrar clientes existentes. O `servidor_captura.py` (extensão) não muda.
</requirements>

## Subtarefas

- [x] 7.1 Escrever os testes de repositório (gravação, leitura, nulos) e de captura com os novos campos.
- [x] 7.2 Criar a migração `0005`.
- [x] 7.3 Atualizar `Vaga`, repositórios, DTO, validador e serviço.
- [x] 7.4 Atualizar os schemas da API de forma aditiva.
- [x] 7.5 Confirmar que os testes de captura existentes continuam passando.

## Detalhes de Implementação

Ver "Modelos de Dados" da techspec. Seguir o formato das migrações existentes em `shared_kernel/adapters/persistence/migracoes/`.

## Critérios de Sucesso

- Vagas capturadas antes da migração continuam sendo listadas.
- A resposta da API inclui os novos campos, nulos quando ausentes.

## Testes da Tarefa

- [x] Testes de unidade e de repositório (com `TEST_DATABASE_URL`).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/prd-job-0047.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/techspec-job-0047.md`
- `src/jobsync/vaga/domain/vaga.py`
- `src/jobsync/vaga/adapters/vaga_repository_impl.py`
- `src/jobsync/vaga/adapters/vaga_repository_fake.py`
- `src/jobsync/vaga/service_layer/capturar_vaga/`
- `src/jobsync/shared_kernel/adapters/persistence/migracoes/`
- `src/jobsync/entrypoints/api/schemas/vaga.py`

# Tarefa 3.0: Persistência tolerante, SalvarPerfilEstruturado e contratos da API do perfil

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Grava e lê os campos novos no JSONB existente, sem migration SQL, e expõe os blocos e as tecnologias incluídas pelos endpoints de perfil.

<requirements>
- `_experiencia_para_json` e `_json_para_experiencia` com `contexto`, `responsabilidades` e `skills`; leitura com `.get(chave, padrão)`, como foi feito com `conquistas`.
- Nenhum arquivo novo em `migracoes/`.
- `SalvarPerfilEstruturado`: DTOs com os campos novos; chama `com_tecnologias_das_experiencias()` antes de persistir; o output traz `tecnologias_incluidas`.
- Schemas Pydantic de `POST/PUT/GET /perfil-estruturado` com os blocos (opcionais, padrão vazio, sem quebrar clientes); resposta do `PUT` com `tecnologias_incluidas: string[]`.
- Log só com contagens (`Tecnologias incluidas pelas skills (quantidade=%d)`), sem texto de currículo.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 3.1 Escrever os testes do repositório, do service e do router (red).
- [x] 3.2 Implementar a serialização tolerante e o service (green).
- [x] 3.3 Implementar schemas e router (green).
- [x] 3.4 Refatorar e rodar `tests/perfil_estruturado` e `tests/entrypoints/api`.

## Detalhes de Implementação

Techspec: "Modelos de Dados" (JSONB), "Endpoints de API" e "Monitoramento e Observabilidade". PRD: RF 11 a 13 e 16 a 20.

Complexidade: medium. Dependências: 2.0.

## Critérios de Sucesso

- JSON antigo, sem os campos novos, é lido sem erro.
- Salvar o perfil inclui as skills ausentes nas tecnologias e informa quais.
- O contrato anterior dos endpoints continua aceito.

## Testes da Tarefa

- [x] Testes do `PerfilEstruturadoRepositoryImpl` (ida e volta e JSON antigo).
- [x] Testes do `SalvarPerfilEstruturado` com repositório fake.
- [x] Testes dos routers do perfil com `TestClient`.
- [x] Regressão: `src/jobsync/tests/perfil_estruturado/` e `src/jobsync/tests/entrypoints/api/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/perfil_estruturado/adapters/perfil_estruturado_repository_impl.py`
- `src/jobsync/perfil_estruturado/adapters/perfil_estruturado_repository_fake.py`
- `src/jobsync/perfil_estruturado/service_layer/salvar_perfil_estruturado/{service,dtos,validator}.py`
- `src/jobsync/entrypoints/api/schemas/perfil_estruturado.py`
- `src/jobsync/entrypoints/api/routers/perfil_estruturado_router.py`
- `src/jobsync/tests/perfil_estruturado/test_perfil_estruturado_repository_impl.py`
- `src/jobsync/tests/perfil_estruturado/test_salvar_perfil_estruturado_service.py`

# Tarefa 5.0: Importação de PDF com os quatro blocos e MigrarExperienciasDoPerfil com endpoint

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

A importação do currículo inicial e a migração de perfis antigos devolvem experiências com os quatro blocos, em rascunho para o usuário revisar.

<requirements>
- `ExtratorPerfilEstruturadoClient`: o prompt exige `descricao` literal, com os rótulos originais preservados.
- `ImportarPerfilDePdf` chama `EstruturarExperienciaService` por experiência, em paralelo (`ThreadPoolExecutor`, máximo de 4).
- Novo service `MigrarExperienciasDoPerfil` (`service.py`, `dtos.py`, `validator.py`, `__init__.py`): para experiências legadas, devolve o rascunho com os blocos e `descricao` vazia, sem persistir; experiências já estruturadas ficam como estão.
- Endpoint `POST /perfil-estruturado/{perfil_identificador}/migracoes-de-experiencias`; `404` se o perfil não existe.
- Um Service não usa outro: ambos usam o domain service.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 5.1 Escrever os testes dos dois services e do router (red).
- [x] 5.2 Ajustar o prompt do extrator e o `ImportarPerfilDePdf` (green).
- [x] 5.3 Implementar `MigrarExperienciasDoPerfil` e o endpoint (green).
- [x] 5.4 Refatorar e rodar `tests/perfil_estruturado` e `tests/entrypoints/api`.

## Detalhes de Implementação

Techspec: "Fluxo de dados", "Endpoints de API" e "Pontos de Integração". PRD: RF 6 a 10 e 15.

Complexidade: medium. Dependências: 3.0, 4.0.

## Critérios de Sucesso

- Importar o exemplo da Starian devolve os quatro blocos sem reescrita do que existia.
- Migrar um perfil antigo não grava nada até o usuário confirmar.
- Tempo da importação dentro do aviso atual de até 1 minuto (verificado na avaliação manual).

## Testes da Tarefa

- [x] Testes de `ImportarPerfilDePdf` (blocos reconhecidos e completados, falha da IA).
- [x] Testes de `MigrarExperienciasDoPerfil` (legada, estruturada, perfil inexistente).
- [x] Testes do router (`404`, contrato).
- [x] Regressão: `src/jobsync/tests/perfil_estruturado/` e `src/jobsync/tests/entrypoints/api/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/perfil_estruturado/adapters/extrator_perfil_estruturado_client.py`
- `src/jobsync/perfil_estruturado/service_layer/importar_perfil_de_pdf/service.py`
- `src/jobsync/perfil_estruturado/service_layer/migrar_experiencias_do_perfil/ (novo)`
- `src/jobsync/entrypoints/api/routers/perfil_estruturado_router.py`
- `src/jobsync/entrypoints/dependencies.py`
- `src/jobsync/tests/perfil_estruturado/test_importar_perfil_de_pdf_service.py`

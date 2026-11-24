# Tarefa 1.0: Backend: Periodo, limite de itens e validação no SalvarPerfilEstruturadoInputValidator

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Valida o formato do período e do ano e o limite de 15 itens na entrada do salvar, com 422, sem tocar nas entidades, e cria a tabela de casos compartilhada com o frontend.

<requirements>
- `Periodo` em `shared_kernel/domain/periodo.py`: lê `início - fim` (`aaaa`, `mmm aaaa` em pt/en ou `mm/aaaa`; fim `Atual`/`Presente`; hífen ou travessão, com ou sem espaços; início não pode ser depois do fim); `PeriodoInvalido(ValueError)` com exemplo na mensagem; `validar_ano` para certificações.
- `LIMITE_DE_ITENS_POR_LISTA = 15` em `perfil_estruturado/domain/perfil_estruturado.py`.
- `SalvarPerfilEstruturadoInputValidator`: valida período de experiências e formações (se preenchido), ano das certificações e o limite em experiências, formações, certificações e idiomas; tecnologias ficam fora; a mensagem cita lista, posição e campo.
- Nenhuma invariante nova nas entidades: o repositório continua lendo perfis salvos com período livre.
- Tabela compartilhada `frontend/src/shared/formulario-curriculo/periodo.casos.json`, lida pelo pytest (e pelo Vitest na task 2.0).
- Log `WARNING` sem texto do currículo.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 1.1 Escrever os testes de `Periodo`, do validator, do router e do repositório (red).
- [x] 1.2 Implementar `Periodo`, `validar_ano` e a constante (green).
- [x] 1.3 Implementar a validação no validator (green).
- [x] 1.4 Refatorar e rodar `tests/perfil_estruturado`, `tests/shared_kernel` e `tests/entrypoints`.

## Detalhes de Implementação

Techspec: "Modelos de Dados", "Endpoints de API" e "Decisões Principais" (validação fora do domínio). PRD: RF 21 a 24.

Complexidade: medium. Dependências: nenhuma.

## Critérios de Sucesso

- Período, ano ou quantidade inválidos devolvem 422 com a mensagem do item.
- Perfil salvo antes desta regra, com período livre, continua sendo lido.
- O contrato anterior aceita dados válidos sem mudança.

## Testes da Tarefa

- [x] Testes de `TestPeriodo` (tabela de casos).
- [x] Testes do `SalvarPerfilEstruturadoInputValidator` (período, ano, 16 itens, tecnologias acima de 15, vazio aceito).
- [x] Teste do repositório lendo período livre.
- [x] Testes do router (422).
- [x] Regressão: `src/jobsync/tests/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/shared_kernel/domain/periodo.py (novo)`
- `src/jobsync/perfil_estruturado/domain/perfil_estruturado.py`
- `src/jobsync/perfil_estruturado/service_layer/salvar_perfil_estruturado/validator.py`
- `frontend/src/shared/formulario-curriculo/periodo.casos.json (novo)`
- `src/jobsync/tests/shared_kernel/test_periodo.py (novo)`
- `src/jobsync/tests/perfil_estruturado/test_salvar_perfil_estruturado_service.py`
- `src/jobsync/tests/entrypoints/api/test_perfil_estruturado_router.py`

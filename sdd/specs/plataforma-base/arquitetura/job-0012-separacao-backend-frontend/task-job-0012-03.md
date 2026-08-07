# Tarefa 03: Mapear casos de uso para services e DTOs

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar a ponte entre schemas de API e os casos de uso do `service_layer`, sem alterar regras de negócio.

<requirements>
- Criar schemas Pydantic `*Request` e `*Response` em `src/jobsync/entrypoints/api/schemas/<dominio>.py`.
- Garantir que cada endpoint traduza request para o `InputDto` do Service e resposta a partir do `OutputDto`.
- Manter validações de formato no schema; regras de negócio no Service/domínio.
- Não usar entidades de domínio como `response_model`.
</requirements>

## Subtarefas

- [ ] 3.1 Mapear todos os `Service.executar` existentes e seus DTOs.
- [ ] 3.2 Criar schemas de request/response iniciais para cada domínio.
- [ ] 3.3 Escrever conversores de/para DTOs (pode ser função ou método de schema).
- [ ] 3.4 Validar com testes unitários de schemas.

## Detalhes de Implementação

Ver `techspec-job-0012.md` -> Design de Implementação -> Modelos de Dados. Seguir `back-end-general-rules.md` sobre Pydantic e `code-design-standards.md` sobre DTOs.

## Critérios de Sucesso

- Todo schema Pydantic tem `Field(description=...)` nos campos públicos.
- Não há entidade de domínio sendo usada diretamente como `response_model`.
- Conversores mantêm invariância de domínio.

## Testes da Tarefa

- [ ] Testes unitários de schemas (payloads inválidos rejeitados).
- [ ] Testes de conversão request -> `InputDto` -> `OutputDto` -> response.
- [ ] `pytest` e `lint-imports` passam.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/schemas/`
- `src/jobsync/*/service_layer/*/dtos.py`
- `src/jobsync/*/service_layer/*/service.py`

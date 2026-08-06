# Tarefa 3.0: Migrar domínios folha ats_score e token_captura

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Migrar os domínios sem dependências cruzadas (`ats_score` e `token_captura`) para a nova estrutura `src/jobsync/<dominio>/{domain,service_layer,adapters}`, validando a organização por camadas.

<requirements>
- Criar `jobsync/ats_score/domain`, `service_layer`, `adapters`.
- Criar `jobsync/token_captura/domain`, `service_layer`, `adapters`.
- Renomear `use_case.py` para `service.py` e manter o método `executar`.
- Garantir que `domain` não dependa de infraestrutura.
- Ajustar e mover os testes correspondentes.
</requirements>

## Subtarefas

- [x] 3.1 Migrar `ats_score`: domain, service_layer, adapters.
- [x] 3.2 Migrar `token_captura`: domain, service_layer, adapters.
- [x] 3.3 Ajustar imports e `__init__.py` de compatibilidade.
- [x] 3.4 Mover/ajustar testes para `src/jobsync/tests/ats_score/` e `token_captura/`.

## Detalhes de Implementação

Ver `techspec.md` → Sequenciamento de Desenvolvimento → Domínios folha. Estes domínios são simples e permitem validar a divisão em camadas antes dos domínios core.

## Critérios de Sucesso

- `pytest` passa para `ats_score` e `token_captura`.
- `domain` não importa `adapters`, `infrastructure` nem `service_layer`.
- Camada `adapters` implementa ports de `domain`.

## Testes da Tarefa

- [ ] `pytest src/jobsync/tests/ats_score/`
- [ ] `pytest src/jobsync/tests/token_captura/`
- [ ] `import-linter` sem ciclos nestes domínios.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes
- `src/domain/ats_score/`
- `src/domain/token_captura/`
- `src/jobsync/ats_score/`
- `src/jobsync/token_captura/`

# Tarefa 5.0: Migrar domínios de negócio

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Migrar `candidatura` e `perfil_estruturado` para a nova arquitetura, garantindo que `candidatura` referencie `curriculo` e `vaga` apenas por ID e que `perfil_estruturado` mantenha a extração de PDF.

<requirements>
- Criar `jobsync/candidatura/{domain,service_layer,adapters}`.
- Criar `jobsync/perfil_estruturado/{domain,service_layer,adapters}`.
- Em `candidatura`, garantir referências por ID a outros domínios.
- Mover casos de uso para `service_layer` com `executar`.
- Criar/adjustar repositórios `Impl`.
- Mover e ajustar testes.
</requirements>

## Subtarefas

- [ ] 5.1 Migrar `candidatura`: `Candidatura`, `StatusCandidatura`, `MudancaStatus`, repositório.
- [ ] 5.2 Migrar casos de uso de `candidatura` para `service_layer`.
- [ ] 5.3 Migrar `perfil_estruturado`: entidades, extração de PDF.
- [ ] 5.4 Criar repositórios `Impl` e clients externos.
- [ ] 5.5 Mover testes para `src/jobsync/tests/candidatura/` e `perfil_estruturado/`.

## Detalhes de Implementação

Ver `techspec.md` → Domínios de negócio. `candidatura` não pode depender de entidades de `curriculo` ou `vaga` diretamente — apenas IDs e value objects de `shared_kernel`.

## Critérios de Sucesso

- `pytest` passa para `candidatura` e `perfil_estruturado`.
- Nenhum `domain/model.py` de `candidatura` importa `domain/model.py` de outro domínio.
- Serviços recebem repositórios/ports por injeção.

## Testes da Tarefa

- [ ] `pytest` por domínio.
- [ ] Testes de mudança de status e regras de domínio.
- [ ] `import-linter` sem import proibido.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes
- `src/domain/candidatura/`
- `src/domain/perfil_estruturado/`
- `src/infrastructure/persistence/`
- `src/infrastructure/extractors/`

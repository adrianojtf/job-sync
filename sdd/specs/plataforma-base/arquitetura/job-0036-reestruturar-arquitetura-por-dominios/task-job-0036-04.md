# Tarefa 4.0: Migrar domínios com persistência simples

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Migrar `perfil`, `curriculo_salvo` e `vaga` para a estrutura por domínios, extraindo repositórios do `infrastructure/persistence` e organizando casos de uso em `service_layer/<funcionalidade>/`.

<requirements>
- Criar `jobsync/perfil/`, `jobsync/curriculo_salvo/`, `jobsync/vaga/` com as três camadas.
- Criar interfaces de repositório em `domain` e implementações `Impl` em `adapters`.
- Mover entidades, value objects, ports, validators e exceptions para `domain`.
- Mover casos de uso para `service_layer/<funcionalidade>/` com `service.py`, `dtos.py`, `validator.py` e `__init__.py`.
- Ajustar testes para o novo path.
</requirements>

## Subtarefas

- [x] 4.1 Migrar domínio `perfil` (entidades, repositório, services).
- [x] 4.2 Migrar domínio `curriculo_salvo` (salvar/listar/remover).
- [x] 4.3 Migrar domínio `vaga` (`Vaga`, `AnaliseVaga`, repositório, análise).
- [x] 4.4 Criar/adjustar `__init__.py` de reexportação.
- [x] 4.5 Mover testes para `src/jobsync/tests/{perfil,curriculo_salvo,vaga}/`.

## Detalhes de Implementação

Ver `techspec.md` → Componentes `perfil`, `curriculo_salvo`, `vaga` e Design de Implementação. Repositórios devem ter sufixo `Impl` e representar agregados completos.

## Critérios de Sucesso

- Testes de `perfil`, `curriculo_salvo` e `vaga` passam.
- `domain` não importa `adapters` nem `infrastructure`.
- `service_layer` não instancia adapters concretos (recebe ports por injeção).

## Testes da Tarefa

- [ ] `pytest` por domínio.
- [ ] Testes de repositório `Impl` com banco SQLite em memória.
- [ ] `import-linter` valida camadas.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes
- `src/domain/perfil/`
- `src/domain/curriculo_salvo/`
- `src/domain/vaga/`
- `src/infrastructure/persistence/`
- `src/application/use_cases/` (referência dos casos de uso)

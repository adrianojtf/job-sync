# Tarefa 9.0: Configurar import-linter e testes de arquitetura

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Adicionar contratos `import-linter` para garantir a conformidade com a arquitetura por domínios e evitar dependências proibidas e ciclos. Integrar a checagem em CI/PR.

<requirements>
- Configurar `import-linter` em `pyproject.toml` ou `setup.cfg`.
- Criar contratos para: `domain` isolado, `service_layer` sem adapters concretos, `adapters` via ports, `entrypoints` sem `domain` direto e ausência de ciclos.
- Ajustar qualquer violação remanescente.
- Adicionar execução `lint-imports` na checagem de CI/PR.
- Criar testes de arquitetura adicionais se necessário.
</requirements>

## Subtarefas

- [ ] 9.1 Definir contratos `import-linter` para todas as camadas e domínios.
- [ ] 9.2 Rodar `lint-imports` e corrigir violações.
- [ ] 9.3 Adicionar `lint-imports` ao CI/PR.
- [ ] 9.4 Adicionar testes de arquitetura (ex: pytest de importação).

## Detalhes de Implementação

Ver `techspec.md` → Testes de arquitetura. Contratos devem proibir `domain` de importar `adapters`, `service_layer` de outro domínio ou `infrastructure`; `entrypoints` não importa `domain` diretamente.

## Critérios de Sucesso

- `lint-imports` passa sem violações.
- Ciclos de importação entre domínios são bloqueados.
- CI/PR executa `lint-imports`.

## Testes da Tarefa

- [ ] `lint-imports` passa.
- [ ] `pytest` geral passa.
- [ ] Pipeline de CI/PR falha em violação proposital (sanity check).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes
- `pyproject.toml` ou `setup.cfg`
- `.github/workflows/` (ou equivalente de CI)
- `src/jobsync/**/__init__.py`

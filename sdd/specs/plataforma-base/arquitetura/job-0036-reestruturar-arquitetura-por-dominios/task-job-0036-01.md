# Tarefa 1.0: Preparar ambiente de migração

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar a estrutura base `src/jobsync/`, ajustar a configuração do `pytest`, o `PYTHONPATH` e adicionar o `import-linter` para permitir a migração incremental por domínio sem quebrar a suíte de testes.

<requirements>
- Criar o pacote raiz `src/jobsync/` com `__init__.py`.
- Ajustar `pytest.ini` para apontar o `pythonpath` para o novo layout.
- Adicionar `import-linter` em `requirements.txt`.
- Garantir que `pytest` ainda rode com o ambiente legado (baseline verde).
</requirements>

## Subtarefas

- [ ] 1.1 Criar `src/jobsync/__init__.py` e estrutura de diretórios base.
- [ ] 1.2 Atualizar `pytest.ini` e o `PYTHONPATH` para reconhecer `src/jobsync/`.
- [ ] 1.3 Adicionar `import-linter` em `requirements.txt`.
- [ ] 1.4 Rodar `pytest` e confirmar baseline verde.

## Detalhes de Implementação

Ver `techspec.md` → Sequenciamento de Desenvolvimento → Pré-migração. O foco é garantir o novo `pythonpath` antes de mover qualquer domínio, de modo que cada PR subsequente possa manter `pytest` passando.

## Critérios de Sucesso

- `pytest` passa no estado legado.
- `import-linter` está instalado e pode ser executado.
- `src/jobsync/` é um pacote Python importável.

## Testes da Tarefa

- [ ] `pytest` passa.
- [ ] `lint-imports --config setup.cfg` (ou equivalente) roda sem erros.
- [ ] Importação de `jobsync` não levanta `ModuleNotFoundError`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes
- `src/jobsync/__init__.py`
- `pytest.ini`
- `requirements.txt`
- `src/domain/__init__.py` (referência de origem)

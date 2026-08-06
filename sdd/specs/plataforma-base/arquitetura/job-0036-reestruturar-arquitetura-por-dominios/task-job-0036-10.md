# Tarefa 10.0: Limpar diretórios legacy e atualizar README

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Após validar que todos os domínios, entrypoints e testes estão migrados e passando, remover os diretórios legados (`src/application`, `src/domain`, `src/infrastructure`, `src/ui`, `src/tests` antigo) e atualizar o `README.md` com a nova estrutura de pastas.

<requirements>
- Verificar que nenhum código legado é referenciado pelos novos arquivos.
- Remover `src/application/`, `src/domain/`, `src/infrastructure/`, `src/ui/`, `src/tests/` (legacy).
- Atualizar `README.md` com o novo layout `src/jobsync/<dominio>/{domain,service_layer,adapters}`.
- Manter `pytest` e `lint-imports` passando após a limpeza.
</requirements>

## Subtarefas

- [ ] 10.1 Verificar que nenhum import legado resta.
- [ ] 10.2 Remover diretórios legados.
- [ ] 10.3 Atualizar `README.md`.
- [ ] 10.4 Rodar `pytest` e `lint-imports` finais.

## Detalhes de Implementação

Ver `techspec.md` → Limpeza e Monitoramento. A remoção só ocorre após validação para permitir `git bisect` e rollback.

## Critérios de Sucesso

- `pytest` passa sem diretórios antigos.
- `lint-imports` passa.
- `README.md` reflete a estrutura `src/jobsync/`.

## Testes da Tarefa

- [ ] `pytest` completo.
- [ ] `lint-imports`.
- [ ] Conferência manual dos paths legados.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes
- `src/application/`
- `src/domain/`
- `src/infrastructure/`
- `src/ui/`
- `src/tests/`
- `README.md`

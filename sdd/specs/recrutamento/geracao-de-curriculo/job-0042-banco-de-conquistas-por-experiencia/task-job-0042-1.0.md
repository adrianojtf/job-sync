# Tarefa 1.0: Conquista no domínio da experiência e persistência no JSONB

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cria o Value Object `Conquista` e o guarda dentro de `ExperienciaProfissional`, com a regra de similaridade textual, e persiste a lista no JSONB `experiencias_json` sem migração de schema.

<requirements>
- `OrigemConquista` (MANUAL, RESPOSTA_PERGUNTA) e `Conquista(texto, origem)` em `perfil_estruturado.py`; texto vazio é rejeitado.
- `ExperienciaProfissional.conquistas: tuple[Conquista, ...] = ()`; conquistas iguais após normalização na mesma experiência são rejeitadas.
- `conquistas_parecidas.py` com `sao_parecidas(texto_a, texto_b)`: minúsculas, sem acento e pontuação, sobreposição de palavras com limite em constante nomeada (inicial 0,6).
- `ExperienciaProfissional.conquistas_parecidas_com(texto)`.
- `PerfilEstruturadoRepositoryImpl` serializa e lê `conquistas` explicitamente; linha antiga sem a chave volta com lista vazia.
- Exportar `Conquista` e `OrigemConquista` no `__init__` do pacote, como as demais classes do perfil.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 1.1 Escrever os testes de `Conquista` e de `ExperienciaProfissional` (red): texto vazio, duplicata, parecidas com paráfrase, caixa e acento.
- [x] 1.2 Escrever os testes de `sao_parecidas` (red) e implementar a função (green).
- [x] 1.3 Implementar `Conquista`, `OrigemConquista` e o campo `conquistas` (green).
- [x] 1.4 Escrever os testes de integração do repositório (red): salvar e ler com conquistas; ler linha sem a chave `conquistas`.
- [x] 1.5 Implementar a serialização e a leitura no repositório (green).
- [x] 1.6 Refatorar e rodar os testes de `perfil_estruturado`.

## Detalhes de Implementação

Techspec: "Interfaces Principais", "Modelos de Dados" e "Decisões Principais" (JSONB dentro da experiência, duplicidade no domínio). PRD: RF 1, 3, 4, 5 e 6. Atenção: o `__dict__` atual não serializa o `Conquista` aninhado.

## Critérios de Sucesso

- Perfis salvos antes da entrega abrem sem alteração e sem migração.
- O texto da conquista nunca é vazio e não há duplicata na experiência.
- Nenhum teste existente de `perfil_estruturado` quebra.

## Testes da Tarefa

- [x] Testes de unidade do domínio e da similaridade.
- [x] Testes de integração do repositório (fixture `pool_postgres`).
- [x] Regressão: `src/jobsync/tests/perfil_estruturado/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/perfil_estruturado/domain/perfil_estruturado.py`
- `src/jobsync/perfil_estruturado/domain/conquistas_parecidas.py (novo)`
- `src/jobsync/perfil_estruturado/adapters/perfil_estruturado_repository_impl.py`
- `src/jobsync/perfil_estruturado/__init__.py`
- `src/jobsync/tests/perfil_estruturado/test_perfil_estruturado.py`
- `src/jobsync/tests/perfil_estruturado/test_perfil_estruturado_repository_impl.py`

## Resultado da execução

- `Conquista`, `OrigemConquista`, `conquistas_parecidas.py` (limite 0,6) e o campo `conquistas` em `ExperienciaProfissional`; serialização explícita no JSONB, com leitura retrocompatível.
- Testes: `src/jobsync/tests/perfil_estruturado/` passando (inclui integração com PostgreSQL).

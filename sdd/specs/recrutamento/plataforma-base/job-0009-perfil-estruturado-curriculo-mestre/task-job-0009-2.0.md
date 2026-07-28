# Tarefa 2.0: Persistência — schema SQLite + PerfilEstruturadoRepositoryImpl

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Adicionar a tabela `perfil_estruturado` ao schema compartilhado e implementar `PerfilEstruturadoRepositoryImpl`, persistindo uma linha por perfil (upsert), com as sub-listas serializadas como JSON.

<requirements>
- Adicionar a tabela `perfil_estruturado` a `_SCHEMA` em `src/infrastructure/persistence/_conexao_sqlite.py` (ver DDL exato na seção "Modelos de Dados" da techspec).
- `PerfilEstruturadoRepositoryImpl(caminho_banco: str)`: implementa `PerfilEstruturadoRepository`.
- `salvar`: usa `INSERT ... ON CONFLICT(perfil_identificador) DO UPDATE` (upsert real) — chamar duas vezes para o mesmo `perfil_identificador` deve atualizar, nunca duplicar linha.
- `buscar_por_perfil`: retorna `None` se não existir; caso exista, desserializa as sub-listas JSON de volta para as tuplas de entidades correspondentes.
- Serialização via `json.dumps([dataclasses.asdict(e) for e in tupla])`; desserialização reconstruindo cada dataclass a partir do dict (atenção ao `NivelIdioma`, que precisa ser convertido de/para string no JSON, já que `Enum` não é serializável diretamente).
- Complexidade: medium (serialização/desserialização de múltiplas sub-listas, incluindo o enum `NivelIdioma`).
</requirements>

## Subtarefas

- [ ] 2.1 Adicionar a tabela `perfil_estruturado` a `_SCHEMA` em `_conexao_sqlite.py`.
- [ ] 2.2 Implementar `PerfilEstruturadoRepositoryImpl.salvar` (upsert) em `src/infrastructure/persistence/perfil_estruturado_repository_impl.py`.
- [ ] 2.3 Implementar `PerfilEstruturadoRepositoryImpl.buscar_por_perfil`, incluindo desserialização de todas as sub-listas.
- [ ] 2.4 Escrever testes de integração cobrindo round-trip completo (salvar e buscar, incluindo listas vazias e com múltiplas entradas) e o comportamento de upsert.

## Detalhes de Implementação

Consultar a seção "Modelos de Dados" de `techspec-job-0009.md` para o DDL exato. Seguir o estilo de `src/infrastructure/persistence/curriculo_salvo_repository_impl.py` e `_conexao_sqlite.py` já existentes.

## Critérios de Sucesso

- `salvar` seguido de `buscar_por_perfil` retorna um `PerfilEstruturado` idêntico ao salvo, incluindo todas as sub-entidades.
- Salvar duas vezes para o mesmo `perfil_identificador` atualiza a única linha existente (upsert), nunca duplica.
- `buscar_por_perfil` para um identificador inexistente retorna `None`.

## Testes da Tarefa

- [ ] Teste de integração: salvar e buscar um perfil completo (todas as sub-listas com pelo menos uma entrada) — round-trip idêntico.
- [ ] Teste de integração: salvar e buscar um perfil com todas as sub-listas vazias.
- [ ] Teste de integração: salvar duas vezes o mesmo `perfil_identificador` com dados diferentes — busca retorna a versão mais recente, sem duplicar linha.
- [ ] Teste de integração: buscar um `perfil_identificador` inexistente retorna `None`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/infrastructure/persistence/_conexao_sqlite.py`
- `src/infrastructure/persistence/perfil_estruturado_repository_impl.py`
- `src/tests/infrastructure/persistence/test_perfil_estruturado_repository_impl.py`

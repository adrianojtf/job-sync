# Tarefa 3.0: Repositórios com tipos especiais: currículo salvo e perfil estruturado

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Converte os repositórios que usam dados binários e JSON, que exigem conversão de tipos no driver.

<requirements>
- `curriculo_salvo.pdf_bytes` em `BYTEA`: a leitura devolve `bytes` com o mesmo conteúdo gravado.
- `perfil_estruturado`: listas em `JSONB` via `Jsonb(...)`; remover `json.dumps` e `json.loads`; manter o upsert `ON CONFLICT`.
- Ordenação de `curriculo_salvo` por `data_upload DESC` preservada.
- Testes de ida e volta com PDF binário e com todas as sub-listas do perfil.
</requirements>

## Subtarefas

- [ ] 3.1 Adaptar e ampliar os testes (PDF de ida e volta, JSON de ida e volta, upsert) (red).
- [ ] 3.2 Converter `CurriculoSalvoRepositoryImpl`.
- [ ] 3.3 Converter `PerfilEstruturadoRepositoryImpl`.
- [ ] 3.4 Confirmar que `Idioma.nivel` continua gravado e lido pelo nome do enum.

## Detalhes de Implementação

Techspec: "Modelos de Dados" e Riscos (tipos retornados pelo driver). PRD: RF-01, RF-07.

## Critérios de Sucesso

- Bytes do PDF idênticos após gravar e ler.
- Perfil estruturado completo idêntico após gravar e ler.

## Testes da Tarefa

- [ ] `test_curriculo_salvo_repository_impl` e `test_perfil_estruturado_repository_impl` sobre Postgres real.
- [ ] Regressão: services de currículo salvo e perfil estruturado.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo_salvo/adapters/curriculo_salvo_repository_impl.py`
- `src/jobsync/perfil_estruturado/adapters/perfil_estruturado_repository_impl.py`
- `src/jobsync/tests/curriculo_salvo/`, `src/jobsync/tests/perfil_estruturado/`

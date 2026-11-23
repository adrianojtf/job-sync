# Tarefa 7.0: Vínculo com a candidatura e atualização do PDF salvo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Liga o currículo adaptado ao `curriculo_salvo` criado na confirmação da candidatura e faz a edição posterior atualizar o PDF da candidatura.

<requirements>
- `POST /candidaturas-ajustadas` aceita `curriculo_adaptado_id` opcional; após salvar o `curriculo_salvo`, `ConfirmarCandidaturaAjustada` chama `vincular_curriculo_salvo`.
- `CurriculoSalvoRepository` ganha um método para atualizar o PDF (e o nome) de um currículo salvo do perfil, nas implementações Postgres e fake.
- `AtualizarCurriculoAdaptado` atualiza o PDF do `curriculo_salvo` vinculado, na ordem: gerar PDF, atualizar `curriculo_adaptado`, atualizar `curriculo_salvo`.
- Falha no último passo vai para log `warning` e a resposta devolve o PDF novo (política proposta na techspec).
- Currículo salvo já removido: a atualização ignora o vínculo sem erro.
- Candidatura sem `curriculo_adaptado_id` segue como hoje.
</requirements>

## Subtarefas

- [x] 7.1 Testes da confirmação: com e sem `curriculo_adaptado_id`, compensação em falha (red).
- [x] 7.2 Testes do novo método do repositório de `curriculo_salvo`, Postgres e fake (red).
- [x] 7.3 Testes de `AtualizarCurriculoAdaptado`: atualiza o PDF vinculado, vínculo ausente, falha parcial registrada (red).
- [x] 7.4 Implementar o vínculo, o método de repositório e a atualização (green).
- [x] 7.5 Atualizar DTO, schema e router de candidatura ajustada.

## Detalhes de Implementação

Techspec: "Pontos de Integração" e "Riscos Conhecidos". PRD: RF 10 e casos extremos de candidatura vinculada e currículo removido.

## Critérios de Sucesso

- Depois de editar um currículo vinculado, baixar o PDF da candidatura traz o conteúdo editado.
- A confirmação de candidatura existente continua igual quando não há `curriculo_adaptado_id`.

## Testes da Tarefa

- [x] Testes de unidade dos serviços.
- [x] Teste do repositório de `curriculo_salvo` sobre Postgres real (contrato único para o fake e o Postgres).
- [x] Regressão: `src/jobsync/tests/candidatura/` e `src/jobsync/tests/curriculo_salvo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/candidatura/service_layer/confirmar_candidatura_ajustada/`
- `src/jobsync/curriculo_salvo/domain/curriculo_salvo_repository.py`
- `src/jobsync/curriculo_salvo/adapters/`
- `src/jobsync/curriculo_adaptado/service_layer/atualizar_curriculo_adaptado/`
- `src/jobsync/entrypoints/api/routers/candidatura_router.py`

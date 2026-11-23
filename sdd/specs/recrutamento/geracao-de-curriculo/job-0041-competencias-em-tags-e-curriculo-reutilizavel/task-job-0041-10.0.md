# Tarefa 10.0: Currículo adaptado como fonte de outra vaga e E2E do fluxo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Lista os currículos adaptados como fonte em "Ajustar para uma vaga". A adaptação parte do conteúdo salvo, gera um novo currículo adaptado e não altera o original. Fecha com o E2E do fluxo completo.

<requirements>
- `AdaptarCurriculoRequest` aceita `curriculo_adaptado_id` como fonte, alternativa a `perfil_identificador` e `pdf_base64`; a validação exige exatamente uma fonte.
- O router monta o currículo base e as experiências estruturadas a partir do currículo adaptado, no lugar de `montar_curriculo_pre_montado(perfil)` e `_experiencias_do_perfil(perfil)`.
- O currículo adaptado de origem nunca é alterado pela adaptação.
- `useFontesCurriculo` lista os currículos adaptados (`adaptado:<id>`) ao lado de Meu perfil e dos PDFs salvos.
- Decisão a registrar: tratamento das trocas de tecnologia da JOB-0037 ao usar um currículo como base (Questões em Aberto 4 do PRD). Sem decisão, a base trata o texto como original, e isso é documentado.
- E2E em `frontend/e2e` cobrindo gerar, remover uma tag, confirmar, editar, recarregar e reabrir, e usar como base de outra vaga.
</requirements>

## Subtarefas

- [x] 10.1 Testes do backend (red): fonte `curriculo_adaptado_id`, exatamente uma fonte, original intacto, 404 de outro perfil.
- [x] 10.2 Testes de `fonte-curriculo` e `AjustarVagaPage` com a fonte `adaptado` (red).
- [x] 10.3 Alterar schema, DTO e router de adaptação (green).
- [x] 10.4 Alterar `fonte-curriculo.ts` e `SeletorFonteCurriculo` (green).
- [x] 10.5 Escrever o E2E Playwright do fluxo completo.
- [x] 10.6 Rodar a suíte completa de backend, frontend e E2E; atualizar README e Postman se citarem as fontes.

## Detalhes de Implementação

Techspec: "Endpoints de API", "Riscos Conhecidos" e "Abordagem de Testes" (serviço). PRD: RF 13 e 14.

## Critérios de Sucesso

- Escolher um currículo adaptado como fonte gera um novo currículo adaptado e deixa o original igual.
- O E2E do fluxo completo passa.
- Nenhuma regressão nas JOB-0033, JOB-0034, JOB-0035, JOB-0037 e JOB-0040.

## Testes da Tarefa

- [x] Testes de unidade do backend e do frontend.
- [x] E2E Playwright do fluxo completo.
- [x] Regressão completa: `pytest`, `npm test` e a suíte E2E.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/entrypoints/api/schemas/curriculo.py`
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/`
- `frontend/src/features/ajustar-vaga/fonte-curriculo.ts`
- `frontend/src/features/ajustar-vaga/SeletorFonteCurriculo.tsx`
- `frontend/e2e/`

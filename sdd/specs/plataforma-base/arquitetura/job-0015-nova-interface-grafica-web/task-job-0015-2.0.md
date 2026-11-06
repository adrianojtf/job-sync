# Tarefa 2.0: Backend — endpoint "Candidatar" em vaga externa

<critical>Ler os arquivos prd-job-0015.md e techspec-job-0015.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expor na API o caso de uso existente `CandidatarNaVagaExterna` (JOB-0007). Ele gera o currículo adaptado, a nota ATS e a carta para uma vaga descoberta. Hoje só o Streamlit chama esse caso de uso.

- **Complexidade:** medium
- **Dependências:** nenhuma

<requirements>
- Criar `POST /v1/vagas/descobertas/candidaturas`, retornando `200`.
- Request: `vaga` (dados da vaga descoberta), `idioma_alvo`, `cargo_alvo`, `empresa_alvo`, e `perfil_identificador` ou `pdf_base64`.
- Response: `nome_arquivo`, `pdf_base64`, `nota`, `requisitos_faltantes`, `carta`, `url_vaga`.
- Usar o perfil estruturado como `curriculo_pre_montado` quando existir (mesma regra de `/curriculos/{id}/adaptacoes`).
- Extrair o helper `_curriculo_pre_montado` / `_perfil_estruturado` de `curriculo_router.py` para um módulo comum dos routers (DRY), sem mudar o comportamento atual.
- Sem fonte de currículo: `400` em `ProblemaResponse`.
</requirements>

## Subtarefas

- [ ] 2.1 Escrever os testes do router (red): 200 com perfil estruturado, 200 com `pdf_base64`, 400 sem fonte.
- [ ] 2.2 Extrair o helper de currículo pré-montado e manter os testes de `curriculo_router` verdes.
- [ ] 2.3 Criar os schemas `CandidatarVagaExternaRequest` e `CandidatarVagaExternaResponse` em `schemas/vaga_externa.py`.
- [ ] 2.4 Adicionar `ServiceCandidatarNaVagaExternaDep` em `api/dependencies.py`.
- [ ] 2.5 Implementar a rota em `vaga_externa_router.py`.
- [ ] 2.6 Adicionar a requisição na `job-sync.postman_collection.json`.

## Detalhes de Implementação

Ver `techspec-job-0015.md` → "Endpoints de API → Novos (backend)". Os DTOs de entrada e saída estão em `vaga_externa/service_layer/candidatar_na_vaga_externa/dtos.py`. O `pdf_bytes` de saída é devolvido em base64, como em `AdaptarCurriculoResponse`.

## Critérios de Sucesso

- O endpoint aparece em `/docs` com exemplo de request e response.
- O resultado é equivalente ao botão "Candidatar" do Streamlit para a mesma vaga.
- Nenhuma regressão em `/v1/curriculos/{id}/adaptacoes` e `/analises-ats`.

## Testes da Tarefa

- [ ] Testes de unidade do router com fakes do service/LLM (3 cenários acima).
- [ ] Testes existentes de `curriculo_router` continuam passando após a extração do helper.
- [ ] `pytest` e `lint-imports` passam.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/routers/vaga_externa_router.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/entrypoints/api/schemas/vaga_externa.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/vaga_externa/service_layer/candidatar_na_vaga_externa/`
- `src/jobsync/tests/entrypoints/api/`
- `job-sync.postman_collection.json`

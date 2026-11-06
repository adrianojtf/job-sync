# Tarefa 3.0: Refatorar AdaptarCurriculoParaVaga para devolver o rascunho

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

A adaptação via IA deixa de gerar PDF e passa a devolver o `RascunhoCurriculoAdaptado`. Os consumidores legados mantêm o comportamento compondo adaptação + geração de PDF.

<requirements>
- Remover `gerador_pdf` do construtor e `pdf_bytes`/`nome_arquivo` do output; adicionar `rascunho`.
- Mover a montagem da seção de experiências para o agregado (DRY).
- `curriculo_adaptado` continua no output (usado pela carta).
- `POST /curriculos/{id}/adaptacoes` (JSON e `?download=true`) com contrato idêntico.
- `POST /cartas-apresentacao` sem gerar PDF.
- Streamlit compõe adaptação + `GerarPdfCurriculoRevisado`.
- Complexidade: high. Dependências: 1.0, 2.0.
</requirements>

## Subtarefas

- [ ] 3.1 Ajustar testes do caso de uso (Red).
- [ ] 3.2 Refatorar service e DTOs.
- [ ] 3.3 Ajustar DI (`dependencies.py`) e registrar o novo caso de uso.
- [ ] 3.4 Compor no router `/adaptacoes` e no Streamlit.
- [ ] 3.5 Rodar a suíte completa.

## Detalhes de Implementação

Ver "Caso de uso de adaptação (mudanças)" e "Endpoints de API" em `techspec-job-0033.md`.

## Critérios de Sucesso

- Nenhuma geração de PDF dentro da adaptação.
- Contrato de `/adaptacoes` e `/cartas-apresentacao` inalterado (testes de router passando).

## Testes da Tarefa

- [ ] Testes de unidade do caso de uso.
- [ ] Testes de router de regressão.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/entrypoints/streamlit_app.py`
- `src/jobsync/tests/curriculo/test_adaptar_curriculo_para_vaga_service.py`
- `src/jobsync/tests/entrypoints/api/test_routers.py`

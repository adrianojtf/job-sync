# Tarefa 2.0: Adaptação, schemas e API do rascunho com competências

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Faz a adaptação devolver `competencias` estruturadas no rascunho e a API aceitar e devolver o campo, tanto na geração do rascunho quanto na geração do PDF revisado.

<requirements>
- `AdaptarCurriculoParaVaga` converte a seção `TECNOLOGIAS` devolvida pela IA em `competencias` (via `de_texto`).
- Schemas de rascunho (`RascunhoAdaptadoResponse`, `GerarPdfCurriculoRevisadoRequest`) incluem `competencias` (lista de `{nome, tags}`).
- Um rascunho recebido com `competencias` é convertido em `RascunhoCurriculoAdaptado.revisado`, descartando categorias vazias.
- Rascunho sem competências (fonte PDF sem seção de tecnologias) continua válido.
- O contrato antigo (seção `TECNOLOGIAS` em texto) continua aceito na entrada e é convertido.
</requirements>

## Subtarefas

- [x] 2.1 Testes do serviço de adaptação: seção da IA vira `competencias` (red).
- [x] 2.2 Testes de schemas e routers: ida e volta de `competencias`, categorias vazias descartadas, contrato antigo aceito (red).
- [x] 2.3 Alterar `adaptar_curriculo_para_vaga/service.py` (green).
- [x] 2.4 Alterar `RascunhoCurriculoAdaptado.revisado` e os schemas em `entrypoints/api/schemas/curriculo.py` (green).
- [x] 2.5 Atualizar `api/tipos` do frontend com o novo campo, sem alterar telas.
- [x] 2.6 Atualizar a collection Postman se ela cobrir esses endpoints.

## Detalhes de Implementação

Techspec: "Componentes" (modificados), "Fluxo" e "Endpoints de API". PRD: RF 5.

## Critérios de Sucesso

- A resposta de `POST /curriculos/{id}/rascunhos-adaptados` traz `competencias` separadas por categoria.
- `POST /curriculos-revisados` gera o PDF a partir de `competencias`.
- Testes de routers e schemas existentes continuam passando.

## Testes da Tarefa

- [x] Testes de unidade do serviço, schemas e routers.
- [x] Regressão: `src/jobsync/tests/curriculo/` e `src/jobsync/tests/entrypoints/api/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/service.py`
- `src/jobsync/curriculo/domain/rascunho_curriculo_adaptado.py`
- `src/jobsync/entrypoints/api/schemas/curriculo.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `frontend/src/api/tipos`
- `src/jobsync/tests/entrypoints/api/`

# Tarefa 8.0: Telas Descobrir vagas (T8) e Configurações (T10)

<critical>Ler os arquivos prd-job-0015.md e techspec-job-0015.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Entregar a busca de vagas em fontes externas com nota de compatibilidade e a ação "Candidatar", além da tela de Configurações com o token da extensão.

- **Complexidade:** medium
- **Dependências:** 2.0 (endpoint de candidatar), 6.0 (componentes de resultado), 1.0 (token)

<requirements>
- Filtros: termo, currículo de referência (biblioteca), idioma e período (7, 15, 30 dias ou qualquer) (RF9.1).
- Busca: obter o PDF com `GET /v1/curriculos/{id}/conteudo` e chamar `POST /v1/vagas/descobrir`.
- Resultados ordenados por nota, com fonte, data, requisitos faltantes e link original (RF9.2).
- "Candidatar": `POST /v1/vagas/descobertas/candidaturas`, mostrar PDF, nota e carta, e oferecer o link para abrir `url_vaga` em nova aba (`noopener`), sem preencher formulários de terceiros (RF9.3). Decisão: a aba abre pelo clique do usuário, porque navegadores bloqueiam `window.open` feito depois de uma chamada assíncrona longa.
- Sem currículos na biblioteca: estado vazio com link para Meus currículos.
- Configurações: gerar token via `POST /v1/tokens-captura`, botão copiar e instruções da extensão (RF11.1).
</requirements>

## Subtarefas

- [x] 8.1 Escrever os testes (red) e implementar os filtros e a busca em `features/descobrir-vagas/`.
- [x] 8.2 Implementar a lista de resultados e o detalhe dos requisitos.
- [x] 8.3 Implementar "Candidatar", reaproveitando os blocos de resultado da tarefa 6.0.
- [x] 8.4 Escrever os testes (red) e implementar `features/configuracoes/`.

## Detalhes de Implementação

Ver `prd-job-0015.md` → F9 e F11, e `techspec-job-0015.md` → "Decisões Principais" (busca do PDF antes de `/vagas/descobrir`). Referência funcional: `_pagina_vagas` e `_renderizar_token_captura` em `streamlit_app.py`.

## Critérios de Sucesso

- A busca devolve vagas ordenadas da maior para a menor nota.
- "Candidatar" gera os artefatos e oferece o link que abre a vaga original em nova aba.
- O token gerado funciona na extensão Chrome sem mudanças nela.

## Testes da Tarefa

- [x] Testes de unidade: busca sem termo mostra erro; resultados aparecem ordenados por nota.
- [x] Testes de unidade: "Candidatar" chama o endpoint novo e mostra o link da vaga original (`target="_blank"`, `rel="noopener"`).
- [x] Testes de unidade: estado vazio sem currículos.
- [x] Testes de unidade: gerar token exibe o valor e copiar usa a área de transferência.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/descobrir-vagas/` (novo)
- `frontend/src/features/configuracoes/` (novo)
- `src/jobsync/entrypoints/api/routers/vaga_externa_router.py`
- `src/jobsync/entrypoints/api/routers/token_captura_router.py`
- `extensao-chrome/popup.js` (referência das instruções)

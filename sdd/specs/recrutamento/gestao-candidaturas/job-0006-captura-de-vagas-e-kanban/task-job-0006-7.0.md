# Tarefa 7.0: Construir a extensão Chrome

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Construir a extensão de navegador Chrome (Manifest V3) que captura o texto da página atual e o envia ao `ServidorCaptura` (Tarefa 6.0), autenticada por um token colado uma única vez pelo usuário.

<requirements>
- `manifest.json` (Manifest V3) com permissão de `activeTab` e `storage` (para guardar o token localmente).
- `content.js`: extrai o texto principal da página (`document.body.innerText`, heurística genérica — sem seletores por site).
- `background.js` (service worker): recebe o texto do content script e faz `POST` para `http://localhost:8502/api/vagas/capturar` com o token salvo.
- `popup.html`: interface simples para colar/salvar o token de captura e mostrar confirmação de "vaga capturada" — complexidade: medium.
</requirements>

## Subtarefas

- [x] 7.1 Criar `extensao-chrome/manifest.json` (Manifest V3).
- [x] 7.2 Criar `extensao-chrome/content.js` com a extração de texto da página.
- [x] 7.3 Criar `extensao-chrome/background.js` com o envio HTTP autenticado ao `ServidorCaptura`.
- [x] 7.4 Criar `extensao-chrome/popup.html` (+ script associado) para configurar o token e exibir feedback de captura.

## Detalhes de Implementação

Consultar a seção "Visão Geral dos Componentes" (fluxo de captura) de `techspec-job-0006.md`. Não há teste automatizado para a extensão nesta fase — a validação é manual (Tarefa 9.0), carregando a extensão via `chrome://extensions` em modo desenvolvedor.

## Critérios de Sucesso

- A extensão carrega sem erros no Chrome (modo desenvolvedor).
- Clicar em "capturar" na extensão envia o texto da página atual ao servidor e recebe confirmação.

## Testes da Tarefa

- [x] Teste manual: carregar a extensão descompactada no Chrome sem erros no console.
- [x] Teste manual: capturar uma página de teste e confirmar recebimento no `ServidorCaptura` (log ou banco).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `extensao-chrome/manifest.json`
- `extensao-chrome/content.js`
- `extensao-chrome/background.js`
- `extensao-chrome/popup.html`

# Tarefa 9.0: Frontend com sessão por cookie e novos fluxos de entrada

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Trocar a sessão baseada em `localStorage` pela sessão do servidor e entregar as telas de entrada, cadastro, confirmação de e-mail e redefinição de senha. Complexidade: high.

<requirements>
- `SessaoProvider` obtém o usuário por `GET /v1/usuarios/me`; `perfil` vem de `perfil_identificador`; `sair` chama `DELETE /v1/sessoes/atual`.
- Cliente HTTP envia cookies (`credentials`) e trata 401 limpando a sessão e levando a `/entrar`.
- `EntrarPage`: botão "Entrar com Google" (navegação para `/v1/provedores/google/autorizacao?destino=`), formulário de e-mail e senha, links para cadastro e recuperação; exibe erros do parâmetro `erro` a partir de lista fixa de mensagens; mostra o formulário de identificador só quando `GET /v1/provedores` lista `simples`.
- Novas páginas: cadastro, confirmar e-mail (`/confirmar-email?token=`), recuperar senha e redefinir senha.
- Rotas e guardas (`rotas.tsx`, `guardas.tsx`) atualizadas.
- Cabeçalho mostra o usuário logado e a ação de sair.
- Regenerar o tipo do OpenAPI (`api/schema.d.ts`) pelo script já existente.
- Acessibilidade: rótulos, foco e navegação por teclado, como nas telas atuais.
</requirements>

## Subtarefas

- [x] 9.1 Cliente de API e tipos para os novos endpoints.
- [x] 9.2 `SessaoProvider`, guardas e tratamento global de 401.
- [x] 9.3 Nova `EntrarPage`.
- [x] 9.4 Páginas de cadastro, confirmação e redefinição de senha.
- [x] 9.5 Cabeçalho com usuário e sair.
- [x] 9.6 Testes Vitest e ajuste dos testes existentes.

## Detalhes de Implementação

Ver "Componentes existentes alterados" e "Endpoints de API" em `techspec-job-0013.md`. Seguir os componentes de `frontend/src/shared/ui` e os testes de `features/entrar/EntrarPage.test.tsx`.

## Critérios de Sucesso

- Usuário sem sessão cai em `/entrar`; com sessão, segue para a página pedida.
- Recarregar a página mantém a sessão; sair a encerra.
- Mensagens de erro em português, sem detalhes técnicos.
- `npm run lint`, `npm run build` e `npm test` passam.

## Testes da Tarefa

- [x] Testes Vitest das páginas e do `SessaoProvider`

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/sessao/`
- `frontend/src/features/entrar/` e novas features de cadastro e redefinição
- `frontend/src/api/`
- `frontend/src/app/{rotas,guardas}.tsx`

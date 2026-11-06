# Tarefa 4.0: Design system do protótipo, AppShell, rotas e tela Entrar (T1)

<critical>Ler os arquivos prd-job-0015.md e techspec-job-0015.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Converter o visual do protótipo em componentes reutilizáveis, montar a estrutura de navegação e entregar a primeira tela funcional: Entrar, com sessão persistida.

- **Complexidade:** medium
- **Dependências:** 3.0

<requirements>
- `shared/ui/tokens.css` com as variáveis `:root` do protótipo (cores, sombra, raios, tipografia Inter/system-ui).
- Componentes base em CSS Modules: `Button` (primary, secondary, text), `Panel`, `StatCard`, `StatusBadge`, `Modal` (`role="dialog"`, `aria-modal`, fecha com `Esc` e clique fora), `Toast`, `Field`, `EmptyState`, `ScoreDimensions`.
- `AppShell` com menu lateral, topbar com trilha "Workspace / Tela" e menu recolhível abaixo de 700px (RF1.1 a RF1.4).
- Rotas com `react-router` para todas as telas (as não implementadas mostram um placeholder) e guarda de sessão.
- `SessaoProvider` guarda `perfil_identificador` em `localStorage` (com `try/catch`). "Sair" limpa a sessão.
- Tela Entrar chama `GET /v1/perfis/{id}` e redireciona para Visão geral (RF2.1, RF2.2).
- `ErrorBoundary` global.
</requirements>

## Subtarefas

- [x] 4.1 Extrair os tokens do protótipo para `tokens.css`.
- [x] 4.2 Escrever os testes (red) e implementar `Modal` e `Toast`.
- [x] 4.3 Implementar os demais componentes base.
- [x] 4.4 Implementar `AppShell`, as rotas e o `ErrorBoundary`.
- [x] 4.5 Implementar `SessaoProvider` e a guarda de rota.
- [x] 4.6 Implementar a tela Entrar (`features/entrar/`).

## Detalhes de Implementação

Ver `techspec-job-0015.md` → "Visão Geral dos Componentes" (`app/`, `shared/ui/`, `shared/sessao/`) e `prd-job-0015.md` → F1 e F2. Usar `sdd/prototipos/carreira_saas_prototipo.html` como referência visual. Ele é sugestão de design, não precisa ser cópia exata.

## Critérios de Sucesso

- O shell renderizado fica visualmente próximo ao protótipo em 1280px, 1000px e 375px.
- Navegação completa por teclado, com foco visível.
- Recarregar a página mantém a sessão. "Sair" volta para Entrar.

## Testes da Tarefa

- [x] Testes de unidade: `Modal` fecha com `Esc` e clique fora; `Toast` some depois do tempo.
- [x] Testes de unidade: Entrar grava a sessão e redireciona; rota protegida sem sessão vai para Entrar; erro da API aparece em mensagem.
- [x] `npm test`, `npm run lint` e `npm run build` passam.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/prototipos/carreira_saas_prototipo.html`
- `frontend/src/shared/ui/` (novo)
- `frontend/src/shared/sessao/` (novo)
- `frontend/src/app/` (novo)
- `frontend/src/features/entrar/` (novo)

# Resumo de Tarefas de Implementação da Nova Interface Gráfica Web (JOB-0015)

## Tarefas

- [ ] 1.0 Backend: CORS configurável e endpoint de token de captura
- [ ] 2.0 Backend: endpoint "Candidatar" em vaga externa
- [ ] 3.0 Fundação do frontend: projeto, testes, tipos do OpenAPI e ApiClient
- [ ] 4.0 Design system do protótipo, AppShell, rotas e tela Entrar (T1)
- [ ] 5.0 Telas Meu perfil (T3) e Meus currículos (T4)
- [ ] 6.0 Telas Ajustar para uma vaga (T5) e Analisar ATS (T6)
- [ ] 7.0 Telas Vagas salvas (T7) e Candidaturas/Kanban (T9)
- [ ] 8.0 Telas Descobrir vagas (T8) e Configurações (T10)
- [ ] 9.0 Tela Visão geral (T2)
- [ ] 10.0 Entrega: Docker/Nginx, README, E2E, acessibilidade e checagem de contrato

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | CORS + `POST /v1/tokens-captura` | low | — | `TestTokenCapturaRouter` (201, 422); CORS respeita `CORS_ORIGINS` |
| 2.0 | `POST /v1/vagas/descobertas/candidaturas` | medium | — | 200 com perfil estruturado, 200 com `pdf_base64`, 400 sem fonte de currículo |
| 3.0 | Fundação do frontend | high | 1.0, 2.0 | `HttpApiClient` (timeout, 204/404/422/500); `ProblemaResponse → ApiError` |
| 4.0 | Design system, AppShell, Entrar | medium | 3.0 | Entrar grava sessão e redireciona; rota protegida sem sessão volta para Entrar; Modal fecha com `Esc` |
| 5.0 | Meu perfil + Meus currículos | high | 4.0 | Formulário adiciona/remove itens e envia payload; importar PDF pré-preenche; limite de 10 currículos |
| 6.0 | Ajustar para uma vaga + Analisar ATS | high | 5.0 | Validação do modal; dimensões da avaliação; download do PDF; aviso de avaliação indisponível |
| 7.0 | Vagas salvas + Kanban | medium | 6.0 | Criar candidatura remove a vaga da lista; mover cartão invalida a listagem |
| 8.0 | Descobrir vagas + Configurações | medium | 1.0, 2.0, 6.0 | Resultados ordenados por nota; "Candidatar" abre a URL original; token gerado e copiável |
| 9.0 | Visão geral | medium | 5.0, 7.0 | `montarResumo` e `calcularCompletude` (funções puras); estado vazio de primeiro acesso |
| 10.0 | Entrega | medium | 1.0 a 9.0 | Build Docker; E2E dos 2 fluxos; axe sem violações graves; diff de `schema.d.ts` no CI |

## Arquivos de origem

- PRD: `prd-job-0015.md`
- Tech Spec: `techspec-job-0015.md`
- Protótipo: `sdd/prototipos/carreira_saas_prototipo.html`

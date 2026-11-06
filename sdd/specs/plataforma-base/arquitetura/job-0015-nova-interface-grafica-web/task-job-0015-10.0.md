# Tarefa 10.0: Entrega — Docker/Nginx, README, E2E, acessibilidade e checagem de contrato

<critical>Ler os arquivos prd-job-0015.md e techspec-job-0015.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Preparar o frontend para rodar de forma independente e proteger a entrega com testes de ponta a ponta, verificação de acessibilidade e checagem do contrato da API no CI.

- **Complexidade:** medium
- **Dependências:** 1.0 a 9.0

<requirements>
- `frontend/Dockerfile` multi-stage (Node 20 build → Nginx) servindo os estáticos, com fallback de rotas para `index.html`.
- Nginx com `proxy_read_timeout 180s` quando fizer proxy de `/v1`.
- `VITE_API_BASE_URL` documentada. `CORS_ORIGINS` do backend incluindo a origem do frontend.
- README com a seção "Frontend": instalar, rodar, testar, gerar tipos e build Docker.
- E2E com Playwright em `frontend/e2e/`: (1) Entrar → Visão geral vazia → Meu perfil → salvar; (2) Ajustar para uma vaga → baixar PDF → criar candidatura → mover no Kanban.
- Verificação de acessibilidade com axe nas telas principais, sem violações "serious" ou "critical".
- Passo de CI que regenera `schema.d.ts` e falha com `git diff --exit-code`.
- Streamlit continua funcionando sem mudanças.
</requirements>

## Subtarefas

- [x] 10.1 Criar `frontend/Dockerfile` e `nginx.conf`.
- [x] 10.2 Atualizar `README.md` e `.env.example`.
- [x] 10.3 Escrever os 2 cenários E2E (backend com LLM fake ou MSW).
- [x] 10.4 Adicionar a verificação axe aos E2E.
- [x] 10.5 Adicionar a checagem de contrato e os jobs `lint`, `test` e `build` do frontend em `.github/workflows`.

## Detalhes de Implementação

Ver `techspec-job-0015.md` → "Testes de Serviço", "Monitoramento e Observabilidade" e "Riscos Conhecidos" (timeouts). Passar `--trace off` ao Playwright no CI.

## Critérios de Sucesso

- `docker build` do frontend conclui e o container serve a UI conectada ao backend.
- Os 2 fluxos E2E passam.
- O CI falha se o contrato da API mudar sem regenerar os tipos.
- `streamlit run` continua funcionando.

## Testes da Tarefa

- [x] E2E Playwright: 2 cenários passando.
- [x] axe sem violações graves nas telas principais.
- [x] Build Docker do frontend e do backend.
- [x] `pytest` (backend) e `npm test` (frontend) passam.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/Dockerfile`, `frontend/nginx.conf` (novos)
- `frontend/e2e/` (novo)
- `.github/workflows/`
- `README.md`
- `.env.example`
- `Dockerfile` (backend, referência)

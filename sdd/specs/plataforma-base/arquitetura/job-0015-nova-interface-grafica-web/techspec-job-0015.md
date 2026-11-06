# Tech Spec — Nova interface gráfica web do job-sync (JOB-0015)

- **Código**: `JOB-0015`
- **Módulo**: `plataforma-base`
- **Subsistema**: `arquitetura`
- **Status**: Rascunho
- **Baseado em**: [prd-job-0015.md](prd-job-0015.md)
- **Depende de**: [techspec-job-0012.md](../job-0012-separacao-backend-frontend/techspec-job-0012.md)
- **Referência visual**: [carreira_saas_prototipo.html](../../../../prototipos/carreira_saas_prototipo.html)

## Resumo Executivo

A nova UI é uma SPA (Single Page Application) em **React 18 + TypeScript + Vite**. Ela fica na pasta `frontend/` na raiz do repositório e consome apenas a API FastAPI `/v1`. Os tipos de request e response são gerados do `openapi.json` do backend (`openapi-typescript`). Assim, o contrato da API é a fonte única da verdade, e a quebra de um campo aparece na compilação, não em produção.

O frontend segue o mesmo espírito hexagonal do backend. As telas (`features/`) dependem de hooks de caso de uso. Esses hooks dependem de um *port* `ApiClient`, implementado por um *adapter* HTTP. Os tokens visuais do protótipo (`:root` CSS variables) viram o design system em `shared/ui/`. O backend recebe três mudanças pequenas para fechar as lacunas: endpoint de token de captura, endpoint de "Candidatar" em vaga externa e CORS configurável. O Streamlit continua no ar sem mudanças.

**Analogia:** o `openapi.json` funciona como a planta elétrica do prédio. O frontend gera as tomadas a partir da planta. Se alguém mudar a voltagem no backend, o eletricista (o compilador TypeScript) avisa antes de ligar o aparelho.

## Arquitetura do Sistema

### Visão Geral dos Componentes

**Novos (frontend):**

| Componente | Responsabilidade |
|---|---|
| `frontend/` | Projeto Vite + React + TS, com `package.json`, `vite.config.ts` e `tsconfig.json` próprios. |
| `frontend/src/app/` | Bootstrap, roteamento (`react-router`), `QueryClientProvider`, guarda de sessão e `AppShell` (menu lateral + topbar do protótipo). |
| `frontend/src/api/schema.d.ts` | Tipos gerados de `/openapi.json` (não editar à mão). |
| `frontend/src/api/api-client.ts` | *Port*: interface `ApiClient` com um método por operação usada. |
| `frontend/src/api/http-api-client.ts` | *Adapter*: implementação com `fetch`, base URL de `VITE_API_BASE_URL`, timeout e conversão de `ProblemaResponse` em `ApiError`. |
| `frontend/src/shared/ui/` | Design system: `tokens.css` (variáveis do protótipo), `Button`, `Panel`, `StatCard`, `StatusBadge`, `Modal`, `Toast`, `Field`, `EmptyState`, `ScoreDimensions`. |
| `frontend/src/shared/sessao/` | `SessaoProvider`: guarda o `perfil_identificador` em `localStorage` (RF2.2). |
| `frontend/src/shared/arquivos/` | Utilitários `base64 ↔ Blob`, download e leitura de `File` em base64. |
| `frontend/src/features/entrar/` | T1. |
| `frontend/src/features/visao-geral/` | T2: agrega dados de outras queries, sem endpoint novo. |
| `frontend/src/features/perfil/` | T3: formulário com `react-hook-form` (`useFieldArray` para as listas). |
| `frontend/src/features/curriculos/` | T4. |
| `frontend/src/features/ajustar-vaga/` | T5: modal de entrada (protótipo) e página de resultado. |
| `frontend/src/features/analisar-ats/` | T6. |
| `frontend/src/features/vagas-salvas/` | T7. |
| `frontend/src/features/descobrir-vagas/` | T8. |
| `frontend/src/features/candidaturas/` | T9: Kanban. |
| `frontend/src/features/configuracoes/` | T10. |
| `frontend/Dockerfile` | Build multi-stage (Node → Nginx) servindo os estáticos. |

**Modificados (backend):**

| Componente | Mudança |
|---|---|
| `src/jobsync/entrypoints/api/routers/token_captura_router.py` (novo) | `POST /v1/tokens-captura`. |
| `src/jobsync/entrypoints/api/routers/vaga_externa_router.py` | `POST /v1/vagas/descobertas/candidaturas` (expõe `CandidatarNaVagaExterna`). |
| `src/jobsync/entrypoints/api/schemas/token_captura.py` (novo), `schemas/vaga_externa.py` | Schemas das novas operações. |
| `src/jobsync/entrypoints/api/dependencies.py` | `ServiceCriarTokenCapturaDep` e `ServiceCandidatarNaVagaExternaDep`. |
| `src/jobsync/entrypoints/api/main.py` | Registrar o novo router. CORS lê `CORS_ORIGINS` (a variável já existe em `.env.example`) e passa a usar `allow_credentials=False`. |
| `README.md` | Seção "Frontend" com o modo de rodar e de gerar os tipos. |

### Fluxo de dados

1. A página chama um hook de feature (ex.: `useAdaptarCurriculo`).
2. O hook usa `useMutation`/`useQuery` (TanStack Query) e chama `ApiClient`.
3. `HttpApiClient` faz `fetch` para `${VITE_API_BASE_URL}/v1/...`.
4. Se a resposta não for 2xx, o corpo `ProblemaResponse` vira `ApiError { status, title, detail, instance }`, que aparece em toast ou em linha.
5. As mutações invalidam as queries afetadas. Exemplo: criar candidatura invalida `['vagas', perfil]` e `['candidaturas', perfil]`.

## Design de Implementação

### Interfaces Principais

```ts
// frontend/src/api/api-client.ts — port
export interface ApiClient {
  obterOuCriarPerfil(id: string): Promise<Perfil>;
  buscarPerfilEstruturado(id: string): Promise<PerfilEstruturado | null>; // 404 → null
  salvarPerfilEstruturado(p: PerfilEstruturadoInput): Promise<PerfilEstruturado>;
  importarPerfilDePdf(pdfBase64: string): Promise<PerfilEstruturado>;
  listarCurriculos(perfil: string): Promise<CurriculoSalvo[]>;
  salvarCurriculo(i: SalvarCurriculoInput): Promise<CurriculoSalvo>;
  baixarCurriculo(id: string): Promise<CurriculoConteudo>;
  removerCurriculo(id: string): Promise<void>;
  // + avaliarVaga, adaptarCurriculo, gerarCarta, analisarAts, avaliarExperiencia,
  //   listarVagas, capturarVaga, descobrirVagas, candidatarVagaExterna,
  //   listarCandidaturas, criarCandidatura, moverCandidatura, criarTokenCaptura
}
```

```ts
// frontend/src/features/ajustar-vaga/use-ajustar-vaga.ts — caso de uso de UI
export function useAjustarVaga(api: ApiClient) {
  const avaliar = useMutation({ mutationFn: api.avaliarVaga });
  const adaptar = useMutation({ mutationFn: api.adaptarCurriculo });
  const ats = useMutation({ mutationFn: api.analisarAts });
  const carta = useMutation({ mutationFn: api.gerarCarta });
  return { avaliar, adaptar, ats, carta };
}
```

O `ApiClient` chega pelo contexto React (`ApiClientProvider`). Nos testes, um *fake* em memória ou o MSW substitui o adapter, o que segue a inversão de dependência (o "D" de SOLID).

### Modelos de Dados

- **Tipos de API:** gerados (`components['schemas']['CandidaturaResponse']` etc.) e reexportados com nomes de domínio em `api/tipos.ts`.
- **Modelos de view** (só apresentação, sem regra de negócio):
  - `ResumoVisaoGeral { curriculos: number; vagasSalvas: number; candidaturasAtivas: number; emEntrevistaOuOferta: number; atividades: Atividade[] }`, calculado em `features/visao-geral/montar-resumo.ts` como função pura.
  - `Atividade { tipo: 'vaga_capturada' | 'curriculo_salvo' | 'status_candidatura'; descricao: string; data: Date }`, derivada de `data_captura`, `data_upload` e `historico_status`.
  - `CompletudePerfil`: percentual de seções preenchidas do perfil estruturado (7 seções). É um indicador visual, não uma regra de domínio.
- **Status do Kanban:** a ordem `APLICADO → ENTREVISTA → OFERTA → REJEITADO` vem das chaves de `CandidaturasListagemResponse.por_status`. Os rótulos em pt-BR ficam em um mapa de apresentação.
- **Sem banco local.** O único dado persistido no navegador é `perfil_identificador`.

### Endpoints de API

**Consumidos (já existentes, JOB-0012):**

| Tela | Operação |
|---|---|
| T1 | `GET /v1/perfis/{id}` |
| T2 | `GET /v1/curriculos`, `GET /v1/vagas`, `GET /v1/candidaturas`, `GET /v1/perfil-estruturado/{id}` (todos com `perfil_identificador`) |
| T3 | `GET/POST /v1/perfil-estruturado`, `PUT /v1/perfil-estruturado/{id}`, `POST /v1/perfil-estruturado/importacoes`, `POST /v1/experiencias-profissionais/avaliacoes` |
| T4 | `GET/POST /v1/curriculos`, `GET /v1/curriculos/{id}/conteudo`, `DELETE /v1/curriculos/{id}` |
| T5 | `POST /v1/vagas/avaliacoes`, `POST /v1/curriculos/{id}/adaptacoes`, `POST /v1/curriculos/{id}/analises-ats`, `POST /v1/cartas-apresentacao` |
| T6 | `POST /v1/curriculos/{id}/analises-ats` |
| T7 | `GET/POST /v1/vagas`, `POST /v1/vagas/avaliacoes`, `POST /v1/candidaturas` |
| T8 | `POST /v1/vagas/descobrir` (o PDF de referência vem de `GET /v1/curriculos/{id}/conteudo`) |
| T9 | `GET /v1/candidaturas`, `POST /v1/candidaturas/{id}/submissao` |

**Novos (backend):**

- `POST /v1/tokens-captura` → `201`
  - Request: `{ "perfil_identificador": "adriano" }`
  - Response: `{ "token": "...", "perfil_identificador": "adriano" }`
  - Usa `CriarTokenCaptura.executar`.
- `POST /v1/vagas/descobertas/candidaturas` → `200`
  - Request: `{ vaga: VagaDescobertaRequest, idioma_alvo, cargo_alvo, empresa_alvo, perfil_identificador?, pdf_base64? }`
  - Response: `{ nome_arquivo, pdf_base64, nota, requisitos_faltantes[], carta, url_vaga }`
  - Usa `CandidatarNaVagaExterna`. Monta `curriculo_pre_montado` a partir do perfil estruturado, reaproveitando o mesmo helper `_curriculo_pre_montado` de `curriculo_router.py`. Esse helper deve ser extraído para um módulo comum dos routers (DRY).

Os dois seguem `back-end-general-rules.md`: schemas Pydantic separados, `summary`/`description`/exemplos, erros em `ProblemaResponse`.

## Pontos de Integração

- **API job-sync `/v1`:** a única integração. Não há autenticação além do `perfil_identificador`, mantendo o modelo do JOB-0004.
- **CORS:** o backend aceita a origem do frontend via `CORS_ORIGINS`. Em desenvolvimento, o proxy do Vite (`/v1 → http://localhost:8000`) dispensa CORS.
- **Operações de IA (OpenAI GPT Luna 6, Jev):** são síncronas e podem passar de 30 s. O adapter usa um timeout de 180 s nessas rotas e de 15 s nas demais. A UI mostra etapas ("Analisando vaga…", "Gerando PDF…").
- **Tratamento de erros:**
  - `400`/`422`: mensagem em linha no formulário.
  - `404` em perfil estruturado: estado vazio, não erro.
  - `5xx`/timeout: toast com a ação "Tentar novamente".
  - `status_avaliacao_vaga = indisponivel`: aviso informativo, sem bloquear o fluxo.
- **Extensão Chrome:** sem mudança. Ela continua usando `servidor_captura.py` com o token gerado em T10.

## Abordagem de Testes

### Testes Unidade

Ferramentas: **Vitest + Testing Library + MSW** (Mock Service Worker, que simula a API no nível HTTP).

- Funções puras: `montarResumo`, `calcularCompletude`, `base64ParaBlob`, mapeamento de `ProblemaResponse → ApiError`.
- `HttpApiClient`: timeout, URL base, tratamento de 204/404/422/500.
- Componentes por feature, pelo comportamento visível:
  - Entrar grava a sessão e redireciona.
  - O formulário de perfil adiciona e remove experiências e envia o payload correto.
  - O modal "Ajustar para uma vaga" valida os campos obrigatórios (comportamento do protótipo), fecha com `Esc` e mostra as dimensões da avaliação.
  - O Kanban move um cartão e invalida a listagem.
  - Vagas salvas: criar candidatura remove a vaga da lista.
  - A biblioteca bloqueia upload acima de 10 currículos com mensagem.
- Mocks só na fronteira HTTP (MSW). Não há mocks de hooks internos.

**Backend (pytest, seguindo `testing-rules.md`):**
- `TestTokenCapturaRouter`: 201 com token e 422 sem `perfil_identificador`.
- Router de candidatar em vaga externa: 200 com perfil estruturado, 200 com `pdf_base64` e 422 sem nenhuma fonte de currículo (padrão dos routers de currículo).
- Fakes in-memory dos repositórios, como nos testes de API existentes.

### Testes de Serviço

- **E2E com Playwright** (`frontend/e2e/`), contra o backend real com fakes de LLM ou contra MSW:
  1. Entrar → Visão geral vazia → Meu perfil → salvar.
  2. Ajustar para uma vaga → baixar PDF → criar candidatura → mover no Kanban.
- **Contrato:** um script de CI gera `schema.d.ts` de novo e falha se houver diff (`git diff --exit-code`).
- Atualizar `job-sync.postman_collection.json` com os dois endpoints novos.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. **Backend: lacunas.** CORS configurável, `POST /v1/tokens-captura`, `POST /v1/vagas/descobertas/candidaturas` e testes. Vem primeiro porque destrava o contrato completo.
2. **Fundação do frontend.** Scaffold Vite, lint, Vitest, geração de tipos, `ApiClient` e adapter, `tokens.css` e componentes base do protótipo, `AppShell` e roteamento.
3. **T1 Entrar + sessão.** Pré-requisito de todas as telas.
4. **T3 Meu perfil e T4 Meus currículos.** São a fonte de currículo dos demais fluxos.
5. **T5 Ajustar para uma vaga e T6 Analisar ATS.** O fluxo de maior valor.
6. **T7 Vagas salvas e T9 Candidaturas.**
7. **T8 Descobrir vagas.** Depende do endpoint novo do item 1.
8. **T10 Configurações.**
9. **T2 Visão geral.** Agrega dados de todas as anteriores.
10. **Docker, README, E2E e acessibilidade (axe).**

### Dependências Técnicas

- Node.js 20 LTS e npm no ambiente de desenvolvimento e CI.
- Backend JOB-0012 rodando (`uvicorn` ou `Dockerfile` atual) e acessível pelo frontend.
- Chaves OpenAI/TypeSafe só no backend, para testes manuais dos fluxos de IA.

## Monitoramento e Observabilidade

- **Frontend:**
  - `ErrorBoundary` global com tela de falha e botão "Recarregar".
  - Erros de API registrados em `console.error` com `status`, `title` e `instance` (do `ProblemaResponse`), para correlacionar com os logs do backend.
  - Sem ferramenta de telemetria nesta entrega (questão em aberto 6 do PRD).
- **Backend:** os novos endpoints usam o `LOG_LEVEL` existente, com `INFO` na criação de token (sem registrar o valor do token) e `ERROR` em falhas de IA.
- **Nginx:** access log padrão do container.

## Considerações Técnicas

### Decisões Principais

| Decisão | Justificativa | Alternativas rejeitadas |
|---|---|---|
| React + Vite + TS | Ecossistema amplo, build rápido, tipagem do contrato. O protótipo é HTML/CSS simples e se converte direto em componentes. | Next.js: SSR desnecessário para uso pessoal autenticado por identificador. Vue: sem vantagem clara para o projeto. |
| Pasta `frontend/` no mesmo repositório | Um PR muda contrato e cliente juntos. As skills SDD já operam neste repositório. | Repositório separado: duplica CI e quebra a rastreabilidade das specs. |
| Tipos gerados do OpenAPI | Uma só fonte de verdade (DRY) e quebra visível na compilação. | Tipos escritos à mão: divergem com o tempo. |
| TanStack Query | Cache, invalidação e estados de carregamento sem um store global (KISS). | Redux: excesso de estrutura para dados que vêm do servidor. |
| CSS Modules + `tokens.css` do protótipo | Reaproveita as variáveis do protótipo sem nova dependência. | Tailwind/Material UI: reescreveria o design ou imporia outra estética. |
| Indicadores da Visão geral calculados no cliente | Sem endpoint novo (YAGNI). O volume por perfil é pequeno (≤ 10 currículos, dezenas de vagas). | Endpoint `/v1/painel`: adiar até haver volume ou o analytics do JOB-0012. |
| Descobrir vagas busca o PDF antes de chamar `/vagas/descobrir` | Não muda o contrato existente. | Aceitar `curriculo_salvo_id` no backend: melhor em tráfego, mas fica como evolução. |
| Chamadas de IA síncronas com timeout longo | Igual ao comportamento atual da API. | Jobs assíncronos/SSE: complexidade alta para 2 a 4 usuários. |
| Streamlit mantido | Rollback imediato e comparação lado a lado. | Remoção imediata: risco sem ganho. |

### Riscos Conhecidos

| Risco | Mitigação |
|---|---|
| Timeouts em chamadas de IA longas (proxy/Nginx) | `proxy_read_timeout 180s` no Nginx, timeout por rota no adapter e mensagem de "pode levar até 1 minuto". |
| Payloads base64 grandes (PDFs de alguns MB) | Limite de 5 MB no upload, validado na UI. Conversão com `FileReader`. |
| `perfil_identificador` sem autenticação expõe dados de outro perfil por URL | Risco já aceito no JOB-0004 (uso pessoal). Registrar como débito para quando houver autenticação real. |
| Divergência entre `schema.d.ts` e o backend | Verificação de diff no CI. |
| `allow_origins="*"` com `allow_credentials=True` libera qualquer origem com credenciais (o Starlette devolve a origem da requisição) | Ler `CORS_ORIGINS` com a lista de origens permitidas e usar `allow_credentials=False`, já que o frontend não usa cookies. |
| A entidade `Vaga` não tem título/empresa | Mostrar a primeira linha do texto e o domínio da URL (questão em aberto 3 do PRD). |

### Conformidade com Padrões

- `.windsurf/rules/general-rules.md`: Clean Code, SOLID (port `ApiClient` injetado), DRY (tipos gerados, helper de currículo pré-montado extraído), KISS/YAGNI (sem store global, sem endpoint de painel).
- `.windsurf/rules/back-end-general-rules.md`: novos endpoints versionados em `/v1`, schemas Pydantic de request/response, status codes corretos (`201` em criação), `ProblemaResponse`, documentação OpenAPI completa, DI via `Depends`, composition root em `dependencies.py`.
- `.windsurf/rules/code-design-standards.md`: nenhuma mudança em `domain/` ou `service_layer/`. Os routers apenas orquestram services existentes.
- `.windsurf/rules/testing-rules.md`: testes de backend no padrão `Test<Classe>`, AAA separado por linha em branco, mocks só com `unittest.mock`.
- **Desvio documentado:** as regras do projeto cobrem só Python. Para o frontend vale o equivalente: componentes sem regra de negócio, testes pelo comportamento observável e mocks só na fronteira HTTP.

### Arquivos relevantes e dependentes

- `sdd/prototipos/carreira_saas_prototipo.html`
- `src/jobsync/entrypoints/api/main.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/entrypoints/api/routers/*.py`
- `src/jobsync/entrypoints/api/schemas/*.py`
- `src/jobsync/entrypoints/streamlit_app.py` (referência funcional, sem mudanças)
- `src/jobsync/entrypoints/servidor_captura.py` (sem mudanças)
- `src/jobsync/token_captura/service_layer/criar_token_captura/service.py`
- `src/jobsync/vaga_externa/service_layer/candidatar_na_vaga_externa/`
- `src/jobsync/tests/entrypoints/api/`
- `.env.example`, `Dockerfile`, `README.md`, `job-sync.postman_collection.json`

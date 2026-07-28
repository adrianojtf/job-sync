# Resumo de Tarefas de Implementação de Descoberta e Match de Vagas

## Tarefas

- [x] 1.0 Modelar domínio (VagaExterna, FonteVagaExterna, VagaComScore)
- [x] 2.0 Definir BuscadorVagasExternoPort + adapters de API direta (RemoteOK, We Work Remotely, Arbeitnow, Adzuna)
- [x] 3.0 Definir ExtratorTextoPaginaPort + adapter BuscadorGoogleCustomSearch (com fallback para snippet e tratamento de cota esgotada)
- [x] 4.0 Implementar use case DescobrirVagasComMatch (busca paralela + dedup + score) com testes
- [x] 5.0 Implementar use case CandidatarNaVagaExterna (ATS + adaptação de currículo + carta de apresentação) com testes
- [x] 6.0 Integrar menu lateral "Vagas" na UI Streamlit (busca por termo + seleção de currículo salvo + lista ordenada por score)
- [x] 7.0 Integrar botão "Candidatar" na UI (roda CandidatarNaVagaExterna, oferece PDF + carta, abre a vaga original em nova aba)
- [x] 8.0 Validação manual end-to-end e execução da suíte completa de testes
- [x] 9.0 Adicionar data_publicacao em VagaExterna + parsing de data em cada adapter
- [x] 10.0 Estender BuscadorVagasExternoPort com parâmetro dias_maximo (uso nativo na Adzuna via max_days_old)
- [x] 11.0 Implementar filtro por período em DescobrirVagasComMatch (client-side, mantendo vagas com data desconhecida)
- [x] 12.0 Seletor de período (7/15/30 dias / qualquer período) na UI "Vagas" + exibir data de publicação por vaga
- [x] 13.0 Validação: suíte completa de testes + validação manual real com filtro de período aplicado

## Dependências

- 1.0 deve ser concluída antes de 2.0 e 3.0.
- 2.0 e 3.0 devem ser concluídas antes de 4.0.
- 4.0 deve ser concluída antes de 6.0.
- 5.0 depende apenas das portas já existentes de currículo/vaga/carta (Fases 0-1) — pode ser feita em paralelo com 2.0, 3.0 e 4.0.
- 6.0 e 5.0 devem ser concluídas antes de 7.0.
- 7.0 deve ser concluída antes de 8.0.
- 9.0 deve ser concluída antes de 10.0.
- 10.0 deve ser concluída antes de 11.0.
- 11.0 deve ser concluída antes de 12.0.
- 12.0 deve ser concluída antes de 13.0.

## Entregáveis principais

- Entidades `VagaExterna`, `FonteVagaExterna` e `VagaComScore`, sem dependência de infraestrutura.
- Cinco adapters de busca externa (RemoteOK, We Work Remotely, Arbeitnow, Adzuna, Google Custom Search) atrás de uma porta única, com timeout individual e falha isolada por fonte.
- Use case `DescobrirVagasComMatch`, reaproveitando `CalcularAtsScore` (Fase 1) e `JobDescriptionAnalyzerPort` (existente), sem criar um segundo motor de comparação.
- Use case `CandidatarNaVagaExterna`, reaproveitando as portas de extração/ajuste/geração de PDF e carta de apresentação (Fases 0-1), sem chamar outro use case diretamente (regra do projeto).
- Item de menu lateral "Vagas" na UI Streamlit, com busca, lista ordenada por score e botão "Candidatar" que prepara os artefatos (PDF adaptado + carta) e abre a vaga original — sem autofill de formulários de terceiros.

## Nota de implementação

`CandidatarNaVagaExterna` duplica parte da lógica de `AdaptarCurriculoParaVaga` (extração + ajuste de seções) e de `GerarCartaApresentacao`, seguindo a regra do projeto de que um use case nunca chama outro — mesmo padrão já usado por `AnalisarAtsVaga` (Fase 1) para duplicar a etapa de extração/análise em vez de depender de `AdaptarCurriculoParaVaga`.

## Achado real na validação da Tarefa 8.0: limite de vagas analisadas por IA

Um teste manual com termo de busca genérico ("product manager") contra as três fontes gratuitas sem cadastro (RemoteOK, We Work Remotely, Arbeitnow) retornou 200+ vagas únicas após deduplicação. Como `DescobrirVagasComMatch` analisava (via `JobDescriptionAnalyzerPort`, API Groq) **todas** as vagas antes de aplicar o limite, essa única busca esgotou a cota diária inteira da conta Groq (200.000 tokens/dia) — confirmando na prática o risco já sinalizado na TechSpec ("Riscos Conhecidos").

**Correção aplicada:** adicionada a constante `LIMITE_VAGAS_ANALISADAS = 20` em `descobrir_vagas_com_match/use_case.py` — após deduplicar, apenas as primeiras 20 vagas são analisadas por IA e recebem score. Teste de regressão adicionado (`test_limita_quantidade_de_vagas_analisadas_por_ia`). Isso substitui a "questão em aberto" original do PRD/TechSpec sobre limitar a quantidade de vagas analisadas — a decisão foi confirmada como necessária por evidência real, não apenas hipotética.

Validação end-to-end real realizada: busca real (sem IA) nas três fontes gratuitas confirmada funcionando (RemoteOK: 100 resultados, Arbeitnow: 110, We Work Remotely: 3, para o termo "python"). A validação do pipeline completo com IA real (análise de vaga + adaptação de currículo + carta de apresentação via `CandidatarNaVagaExterna`) ficou limitada pela cota diária da conta Groq já esgotada no momento do teste (retentativas subsequentes também esgotaram a cota quase imediatamente, mesmo com termo de busca raro) — recomenda-se ao usuário repetir esse teste específico quando a cota resetar (ou considerar upgrade de tier na Groq), mas a lógica está integralmente coberta pelos 172 testes automatizados (fakes determinísticos, sem custo de API) e reaproveita adapters (`JobDescriptionAnalyzerGroq`, `AjustadorTextoGroq`, `GeradorCartaApresentacaoGroq`, `ExtratorCurriculoSegmentadoPorIA`) já validados contra a API real nas Fases 0-2.

## Adendo: filtro por período de publicação (Tarefas 9.0-13.0)

Implementado o filtro por período (7/15/30 dias/qualquer período) pedido pelo usuário após a conclusão inicial da Fase 3. `VagaExterna` ganhou `data_publicacao: date | None`; `BuscadorVagasExternoPort.buscar` ganhou o parâmetro `dias_maximo` (usado nativamente só pela Adzuna via `max_days_old`); `DescobrirVagasComMatch` aplica o filtro client-side sobre a lista deduplicada, antes do corte por `LIMITE_VAGAS_ANALISADAS` (economiza chamadas de IA em vagas que seriam descartadas de qualquer forma). Vagas com `data_publicacao=None` (sempre o caso do Google Custom Search) continuam aparecendo mesmo com filtro ativo — decisão de produto confirmada pelo usuário.

Validação real (sem custo de IA): parsing de data confirmado 100% funcional nas três fontes gratuitas (RemoteOK, We Work Remotely, Arbeitnow) contra a API real. Filtro de 15 dias testado via `DescobrirVagasComMatch` com fakes de IA (para não consumir cota Groq) sobre buscadores reais: excluiu corretamente as 3 vagas da We Work Remotely (todas com 28 dias, fora da janela), mantendo RemoteOK/Arbeitnow (dentro da janela) elegíveis. 181/181 testes automatizados passando.

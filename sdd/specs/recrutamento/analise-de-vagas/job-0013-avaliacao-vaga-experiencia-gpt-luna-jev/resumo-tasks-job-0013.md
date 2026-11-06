# Resumo de Tarefas de Implementação — JOB-0013

## Visão Geral

Migrar os consumidores atuais de Groq para GPT-6 Luna, adicionar avaliações estruturadas Jev para vagas e experiências, expor os fluxos pela API e integrar as avaliações ao processo de adaptação de currículos estruturados.

## Tarefas

- [x] 1.0 Migrar os adapters atuais para GPT-6 Luna
- [x] 2.0 Criar a integração e os modelos de avaliação Jev
- [x] 3.0 Disponibilizar avaliação de descrição de vaga pela API
- [x] 4.0 Disponibilizar avaliação de experiência pela API
- [x] 5.0 Integrar avaliações ao fluxo de adaptação
- [x] 6.0 Finalizar composição, configuração e regressão

## Detalhamento

| # | Título | Complexidade | Dependências | Testes principais |
|---|---|---|---|---|
| 1.0 | Migrar os adapters atuais para GPT-6 Luna | high | — | Fakes OpenAI; testes de contrato dos seis consumidores; sem chamadas reais |
| 2.0 | Criar a integração e os modelos de avaliação Jev | medium | — | Respostas fakes do SDK; mapeamento de dimensões e normalização 0–100 |
| 3.0 | Disponibilizar avaliação de descrição de vaga pela API | medium | 2.0 | Service e endpoint para as quatro dimensões; validação e falhas do provedor |
| 4.0 | Disponibilizar avaliação de experiência pela API | medium | 2.0 | Service e endpoint contextualizado pela vaga; validação e falhas do provedor |
| 5.0 | Integrar avaliações ao fluxo de adaptação | high | 1.0, 3.0, 4.0 | Ordem das chamadas, nota baixa não bloqueante, avaliações por experiência e fluxo PDF |
| 6.0 | Finalizar composição, configuração e regressão | medium | 1.0–5.0 | Suíte pytest, contratos FastAPI, configuração e import-linter |

## Dependências e questões em aberto

- Configurar `OPENAI_API_KEY` e `TYPESAFE_API_KEY` nos ambientes sem armazenar segredos no repositório.
- Decisão aprovada para a tarefa 5.0: se Jev falhar durante a adaptação, prosseguir e indicar quais avaliações ficaram indisponíveis.
- Confirmar requisitos de retenção e processamento dos dados enviados aos provedores.

## Arquivos de origem

- PRD: `prd-job-0013.md`
- Tech Spec: `techspec-job-0013.md`

# Separar job-sync em backend e frontend

> **Task**: GitHub — Projeto 12 (Job Sync)

## Identificação

- **Código Jira**: `JOB-0012` não tem jira task no github
- **Módulo**: `plataforma-base`
- **Subsistema**: `arquitetura`
- **Resumo da funcionalidade**: em kebab-case, ex. `separar-job-sync-backend-frontend`
- **Requisitos**: descrição da feature, user stories ou listas de comportamento esperado

## Contexto

Hoje o **job-sync** é uma aplicação monolítica (Streamlit + lógica de domínio no mesmo processo/repositório). Separar em dois projetos — **backend** (API + regras de negócio) e **frontend** (cliente independente) — permite evoluir a UI sem acoplamento ao runtime do Streamlit e abre caminho para outros clientes (mobile, extensão) consumirem a mesma API.

## Escopo desta story

⚠️ **Esta story contempla apenas o backend.** O objetivo é **extrair a lógica de negócio (hexágono) e disponibilizar as APIs** que hoje são consumidas internamente pelo Streamlit. **Nenhuma UI nova será construída** nesta etapa.

Incluído:

- Extração/isolamento da lógica de domínio em um projeto de backend independente.
- Exposição das operações de negócio como uma API (endpoints HTTP) consumível por qualquer cliente.
- Contrato de API documentado (ex.: OpenAPI/Swagger) para servir de base ao frontend futuro.
- Deploy independente do backend.

Fora de escopo (ficará para stories futuras):

- Implementação do novo frontend / cliente web.
- Migração ou remoção da UI Streamlit atual.

## Por que

- Reduz o acoplamento entre a lógica de negócio (hexágono) e a camada de apresentação atual.
- Viabiliza a story "Implementar nova UI" (ver issue relacionada) sem reescrever regras de negócio — o frontend passará a consumir as APIs entregues aqui.
- Facilita deploy/escala independente de cada parte.

## Status

💡 **Ideia de backlog.** Ainda sem PRD/TechSpec — decisão arquitetural grande, recomendo passar pelo fluxo `criar-prd` antes de iniciar.

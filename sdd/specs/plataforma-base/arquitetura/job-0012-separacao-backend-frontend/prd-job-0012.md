# PRD — Separar job-sync em backend e frontend (JOB-0012)

- **Código**: `JOB-0012`
- **Módulo**: `plataforma-base`
- **Subsistema**: `arquitetura`
- **Resumo da funcionalidade**: `separacao-backend-frontend`
- **Status**: Rascunho

## Visão Geral

Hoje o `job-sync` é uma aplicação monolítica: a camada de apresentação Streamlit e a lógica de domínio executam no mesmo processo e repositório. Isso acopla evoluções de UI a mudanças no runtime de negócio e dificulta a criação de outros clientes (web, mobile, extensão).

Este PRD cobre a primeira etapa da separação: a entrega de um backend independente que hospeda o hexágono de domínio e expõe as operações de negócio como APIs HTTP. O frontend e a migração da UI Streamlit ficam para stories futuras.

## Objetivos

1. Isolar a lógica de negócio (hexágono) em um projeto de backend independente, sem dependência de Streamlit ou outro framework de apresentação.
2. Expor as operações de negócio como endpoints HTTP consumíveis por qualquer cliente.
3. Disponibilizar um contrato de API documentado (OpenAPI/Swagger) que sirva de base ao desenvolvimento do frontend futuro.
4. Permitir deploy independente do backend.
5. Preservar o comportamento da lógica de domínio existente: nenhuma regra de negócio é alterada nesta story.

## Histórias de Usuário

1. **Como desenvolvedor do frontend futuro**, quero consumir uma API HTTP documentada, para construir a nova UI sem depender de chamadas internas ao Streamlit.
2. **Como arquiteto**, quero que a lógica de domínio viva em um hexágono independente, para permitir múltiplos clientes e deploy separado.
3. **Como DevOps**, quero que o backend seja implantável de forma isolada, para escalar e manter a camada de apresentação sem afetar o serviço de negócio.

## Funcionalidades Principais

### RF1 — Isolar o domínio em projeto de backend independente

Mover a lógica de negócio para um projeto próprio, seguindo a arquitetura hexagonal/DDD já definida em `.windsurf/rules/code-design-standards.md`. Cada domínio deve manter suas camadas `domain/`, `service_layer/` e `adapters/`; a UI Streamlit não pode ser dependência obrigatória do backend.

### RF2 — Expor operações de negócio como endpoints HTTP

Criar uma API REST sobre FastAPI (`entrypoints/`) que orquestra os `Services` existentes. Cada endpoint deve traduzir requisições HTTP em chamadas aos casos de uso do domínio e mapear os resultados para schemas Pydantic de resposta.

### RF3 — Documentar o contrato da API (OpenAPI/Swagger)

Aproveitar a geração automática do FastAPI, complementando com `summary`, `description`, `response_model`, `status_code` e exemplos em todos os schemas públicos. O contrato deve ser acessível em `/docs` e `/openapi.json` sem autenticação em ambiente de desenvolvimento.

### RF4 — Habilitar deploy independente do backend

Preparar configuração mínima para execução/implantação do backend sem o frontend: dependências próprias, variáveis de ambiente, `Dockerfile` e instruções de startup. O backend deve ser capaz de subir sozinho e expor a API na porta configurada.

## Experiência do Usuário

Esta story não introduz uma nova interface de usuário. O "usuário" imediato é o desenvolvedor cliente da API: ele deve ser capaz de ler a documentação interativa, entender os recursos, fazer chamadas de teste e obter respostas previsíveis. O contrato deve ser explícito, versionado (`/v1/`) e estável para que o frontend futuro seja construído em cima dele sem quebras.

## Restrições Técnicas de Alto Nível

- O backend deve ser implementado em Python, seguindo as regras de `.windsurf/rules/code-design-standards.md`, `back-end-general-rules.md` e `general-rules.md`.
- A camada `domain` não pode depender de infraestrutura (DB, HTTP, LLM, UI, arquivos).
- Domínios distintos devem se referenciar apenas por ID; nenhum `domain/model.py` de um domínio importa o de outro.
- Endpoints FastAPI devem usar schemas Pydantic separados para request/response e não expor entidades de domínio diretamente.
- O versionamento da API deve ser visível no path (`/v1/...`).
- Deve ser possível subir o backend sem subir o Streamlit.
- Nenhum endpoint pode retornar 200 com corpo de erro; usar códigos HTTP apropriados e formato de erro padronizado.
- A suíte de testes existente deve continuar passando ou ser adaptada para o novo layout sem perda de cobertura.

## Fora de Escopo

- Implementação do novo frontend / cliente web.
- Migração, substituição ou remoção da UI Streamlit atual.
- Mudanças em regras de negócio, modelos de domínio, contratos de LLM, provedores externos ou banco de dados.
- Autenticação e autorização completa (podem ser placeholders/dependências futuras).
- Otimizações de performance/escala além do deploy isolado inicial.

## Questões em Aberto

1. O backend será um repositório separado ou um pacote/pasta no repositório atual (`backend/` na raiz)? A decisão afeta CI, deploy e versionamento.
2. Quais endpoints serão priorizados na primeira entrega? Depende da ordem de extração dos domínios e dos casos de uso mais críticos para o futuro frontend.
3. Qual será a estratégia de persistência inicial — reutilizar os repositórios SQLite existentes ou introduzir uma nova camada?
4. Haverá necessidade de CORS, rate limiting e autenticação no deploy inicial?

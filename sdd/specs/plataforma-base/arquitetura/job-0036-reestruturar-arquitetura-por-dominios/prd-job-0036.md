# PRD — Reestruturar o projeto para a arquitetura por domínios

- **Código**: `job-0036`
- **Módulo**: `plataforma-base`
- **Subsistema**: `arquitetura`
- **Status**: Rascunho

## Visão Geral

O `src/` do Job Sync está organizado por camadas técnicas globais (`application/use_cases`, `domain`, `infrastructure`, `ui`, `tests`). Essa disposição dificulta a identificação de fronteiras de negócio, aumenta o acoplamento entre conceitos distintos e não reflete o padrão obrigatório definido em `.windsurf/rules/code-design-standards.md`.

Este PRD descreve a refatoração pura de reorganização do código para uma estrutura por domínios, baseada em Arquitetura Hexagonal, DDD e Cosmic Python. O objetivo é alinhar o repositório às regras de design sem alterar comportamento, contratos ou experiência do usuário final.

## Objetivos

1. Alinhar a estrutura de pastas e pacotes às regras do SDD (`code-design-standards.md`, `general-rules.md`, `testing-rules.md`).
2. Reduzir o acoplamento entre domínios, garantindo que cada agregado seja dono de suas regras, entidades e casos de uso.
3. Tornar explícitos os limites de cada domínio (`curriculo`, `candidatura`, `vaga`, `perfil`, `ats_score` etc.).
4. Manter a suíte de testes existente passando, sem mudança de comportamento.
5. Facilitar a manutenção, revisão e evolução do sistema por parte do time técnico.
6. Eliminar imports cíclicos e dependências de `domain` para infraestrutura (IO, DB, HTTP, LLM).

## Histórias de Usuário

1. **Como desenvolvedor do time**, quero encontrar o código de um conceito de negócio dentro de um único domínio, para que eu consiga modificar regras sem impactar áreas adjacentes.
2. **Como tech lead**, quero que a estrutura do projeto reflita a linguagem ubíqua e as regras arquiteturais, para que o onboarding e as revisões sejam mais rápidos e consistentes.
3. **Como arquiteto**, quero que domínios se refiram uns aos outros apenas por ID, para que futuras extrações de serviços sejam possíveis sem retrabalho.

## Funcionalidades Principais

### RF1 — Mapear domínios existentes
Identificar os conceitos de negócio presentes em `src/domain/*` e agrupá-los em domínios de alto nível (ex: `curriculo`, `candidatura`, `vaga`, `perfil`, `ats_score`). Cada domínio deve conter seus próprios `domain/`, `service_layer/` e `adapters/`.

### RF2 — Reorganizar a camada `domain`
Mover cada módulo de `src/domain/*` para `<dominio>/domain/`, garantindo que entidades, value objects, ports (interfaces de repositório e serviços externos), validators e exceptions fiquem na camada correta e sem dependência de infraestrutura.

### RF3 — Reorganizar a camada `service_layer`
Mover cada caso de uso de `src/application/use_cases/*` para `<dominio>/service_layer/<funcionalidade>/`, seguindo a organização por funcionalidade com `service.py`, `dtos.py`, `validator.py` e `__init__.py`. O método público principal deve ser `executar`.

### RF4 — Reorganizar a camada `adapters`
Mover os mecanismos técnicos de `src/infrastructure/*` (persistence, llm, pdf, extractors, fontes_vagas, localizacao) para `<dominio>/adapters/`. Implementações de repository e query devem receber o sufixo `Impl`; clients de serviços externos devem implementar as interfaces de port com sufixo `Client`.

### RF5 — Centralizar entrypoints
Mover `src/ui/app_streamlit.py` e `src/infrastructure/api/servidor_captura.py` para `src/job_sync/entrypoints/`, mantendo-os como adapters de entrada da aplicação.

### RF6 — Extrair `shared_kernel/domain`
Identificar value objects usados por mais de um domínio e movê-los para `shared_kernel/domain/`, evitando duplicação e imports diretos entre domínios.

### RF7 — Reorganizar testes
Reorganizar `src/tests` espelhando a estrutura de domínios, de modo que cada teste acompanhe o domínio e a funcionalidade que valida.

### RF8 — Ajustar configurações e imports
Atualizar `pytest.ini`, paths, imports e configurações afetadas pela mudança de estrutura. Renomear pacotes técnicos remanescentes para linguagem ubíqua, eliminando nomes como `repositories`, `services`, `dto`, `interfaces`.

## Experiência do Usuário

Esta iniciativa não altera a experiência do usuário final. Streamlit, servidor de captura e API permanecem funcionando da mesma forma. A mudança é estritamente interna e visa aumentar a qualidade e a manutenibilidade do código.

## Restrições Técnicas de Alto Nível

- O projeto deve permanecer em Python e seguir as regras de `.windsurf/rules/`.
- Nenhum `domain/model.py` de um domínio pode importar `domain/model.py` de outro domínio.
- Agregados de domínios distintos devem se referenciar apenas por ID.
- Nenhuma classe de `domain` pode depender de infraestrutura (IO, DB, HTTP, LLM).
- Nenhum Service pode importar outro Service; a reutilização deve ocorrer via domain services compartilhados.
- Toda a suíte de testes deve continuar passando após a refatoração.
- A aplicação Streamlit e o servidor de captura devem subir normalmente.
- Contratos de API e comportamentos de negócio não devem ser alterados.

## Fora de Escopo

- Criação de novas funcionalidades.
- Alteração de contratos da API REST ou da interface do Streamlit.
- Promover domínios a Bounded Contexts separados (serviços isolados) — decisão adiada por YAGNI.
- Substituição de bibliotecas, modelos de LLM ou provedores externos.

## Questões em Aberto

1. A ordem de migração dos domínios pode impactar a capacidade de entrega incremental? Caso a entrega única se torne inviável, qual domínio deve ser migrado primeiro?
2. Há value objects hoje em `src/domain/*` que serão candidatos a `shared_kernel/domain`? A lista exata depende de análise de dependências cruzadas.
3. A pasta `src/tests` será replicada espelhando `src/job_sync/` ou será adotada uma estrutura alternativa (ex: `tests/` na raiz)?
4. Quais testes de arquitetura (ex: imports proibidos, ausência de dependências cíclicas) serão adicionados para garantir a conformidade contínua?

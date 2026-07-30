---
trigger: always_on
description: Padrões de design de código (baseados em Cosmic Python + DDD)
globs:
---

# Padrões de Design de Código

Regras obrigatórias de camadas, pacotes e nomenclatura para o projeto job-sync. Baseado em Arquitetura Hexagonal com múltiplos domínios (Cosmic Python) e DDD adaptado para Python.

## Estrutura de Pastas

src/projeto/
├── <dominio_1>/              # ex: curriculo
│   ├── domain/
│   │   ├── model.py           # Entities, Value Objects, Aggregates
│   │   └── exceptions.py
│   ├── service_layer/
│   │   ├── services.py        # casos de uso do próprio domínio
│   │   └── unit_of_work.py
│   └── adapters/
│       └── repository.py      # implementação do repositório
│
├── <dominio_2>/               # ex: candidatura
│   └── (mesma estrutura acima)
│
├── shared_kernel/
│   └── domain/                # Value Objects usados por mais de um domínio
│
└── entrypoints/
    ├── streamlit_app.py       # ou flask_app.py, cli.py
    └── ...

## Fundamentos

- Raiz: `src/projeto/` contém todo o código fonte da aplicação.
- Cada domínio tem suas 3 camadas: `domain`, `service_layer`, `adapters`.
- `shared_kernel/domain` contém Value Objects compartilhados entre domínios.
- `entrypoints` contém UI (CLI, web, API).
- Nomenclatura de camadas (Cosmic Python):
  - `domain` -> regras de negócio puras, sem dependência externa
  - `service_layer` -> casos de uso / application services, orquestra domain
  - `adapters` -> implementações concretas (repository, LLM, PDF)
  - `entrypoints` -> UI, CLI, API (adapters de entrada)
- Classes em `domain` podem depender de bibliotecas Python padrão e libs de domínio puro, **sem** depender de infraestrutura (IO, DB, HTTP, LLM).
- Em `domain` use apenas linguagem ubíqua; sem termos técnicos de infraestrutura.

## Regras de Dependência entre Domínios

1. Um Aggregate referencia outro só por ID, nunca por objeto embutido
   (ex: Candidatura guarda curriculo_id: UUID, não curriculo: Curriculo).

2. Casos de uso que cruzam dois domínios vivem no service_layer do
   domínio "dono" do resultado, e recebem o repositório do outro
   domínio como dependência injetada (porta), nunca como import direto
   de implementação concreta.

3. Nenhum domain/model.py de um domínio importa domain/model.py de
   outro domínio diretamente.

4. Promover um domínio a Bounded Context separado (possível serviço
   isolado) só quando ele ganhar complexidade própria significativa
   (workflow, integrações externas específicas). Não fazer antecipadamente
   — decisão de escala, sujeita a YAGNI.

## Camada: service_layer

Casos de uso / application services. Orquestra o domain e coordena fluxos. Tipos de classe aceitos: `Service` (casos de uso), DTOs de input/output/filter, `Validator` (de input), `Query`, exceptions específicas.

### Service (caso de uso)

- Cada funcionalidade geralmente tem um Service correspondente; a UI (entrypoints) delega para ele.
- **Não criar interface + implementação por padrão**. Em Python, use classes concretas diretamente. Só crie interface quando necessário para testes (mocking) ou polimorfismo.
- Método público preferencial: `executar`.
- Um Service **nunca** pode importar/usar outro Service. Se surgir essa necessidade, extraia um domain service compartilhado.
- Use injeção de dependência via construtor (`__init__`).

Implementação:
- Pacote: `<dominio>/service_layer/<conceito de domínio + funcionalidade>`
- Nome: PascalCase. Ex.: `AdaptarCurriculoParaVaga`.

Organização por funcionalidade (classes fortemente relacionadas do caso de uso ficam juntas). Ex.:

Pacote: `curriculo/service_layer/adaptar_curriculo_para_vaga`
- `service.py` - `AdaptarCurriculoParaVaga`
- `dtos.py` - `AdaptarCurriculoParaVagaInputDto`, `AdaptarCurriculoParaVagaOutputDto`
- `validator.py` - `AdaptarCurriculoParaVagaInputValidator`
- `__init__.py` - Exporta as classes públicas

### DTO de Service

Criar apenas quando necessário. Primitivos, PKs, datas, entidades podem ser usados direto como input/output.

- Use `@dataclass(frozen=True)` para DTOs imutáveis ou `pydantic.BaseModel` para validação automática.
- Sufixos: `InputDto`, `OutputDto`, `Filter`.

1) DTO usado por um único Service: nome do caso de uso + sufixo. No mesmo pacote do Service.
  - `AdaptarCurriculoParaVagaInputDto`, `AdaptarCurriculoParaVagaOutputDto`.

2) DTO reutilizado entre Services do mesmo conceito: nome da entidade/conceito + sufixo. No pacote que agrupa os Services.
  - `CurriculoInputDto`, `CurriculoOutputDto`.

3) Estrutura em árvore: nome da entidade/conceito + sufixo.
  - `CriarTituloInputDto`, `CriarParcelaInputDto`.

UI (entrypoints) **nunca** mapeia entidades diretamente para JSON; sempre converte para DTO.

### Query (interface)

Services se dividem em `command` (alteram estado) e `query` (consultam). Em `command`, sempre use `Repository`. Em `query`, se o repositório não servir (paginação, filtros variados, relatórios, agregações específicas), crie uma `Query`.

- Interface em `<dominio>/service_layer`, implementação concreta em `<dominio>/adapters` (ports and adapters).
- Específica para 1 Service; fica no mesmo pacote do Service.
- 1 único método público: `execute`, recebendo filtros e retornando dados.
- Um Service pode chamar mais de uma `Query`, mas cada `Query` = 1 única consulta.
- Pode retornar entidades de domínio ou estruturas ad-hoc.

Localização:
- Pacote: `<dominio>/service_layer/<pacote do service que usa a query>`
- Nome: verbo no infinitivo + sufixo `Query`. Ex.: `ConsultarVersaoOrcamentoEmpresarialQuery`.

### Validator de Service

Validações básicas de input (obrigatoriedade, formato, existência de chave). Invariantes de negócio devem ficar no domínio, não aqui.

- Pacote: `<dominio>/service_layer/<pacote do service>`
- Nome: nome da estrutura de input + sufixo `Validator`. Ex.: `AdaptarCurriculoParaVagaInputValidator`.
- Comportamento padrão ao detectar inválido: lançar `ValueError` ou exceção específica de validação.

## Camada: domain

Modelo de domínio: entidades, agregados, value objects, repositórios, domain services, domain events, factories, specifications, strategies, decorators, exceptions de domínio etc. Aqui devem ficar a maior parte das regras de negócio e invariantes.

### Organização de subpacotes

- Nomeie pacotes pela linguagem ubíqua do domínio. **Não** use categorias técnicas (`repositories`, `services`, `exceptions`, `dto`, `interfaces`).
- Agrupe classes fortemente coesas (mudam/são reutilizadas juntas) no mesmo pacote. Raízes de agregado geralmente nomeiam os pacotes.
- Ex.: `domain.curriculo` contém `Curriculo`, `SecaoCurriculo`, `TipoSecao`, validators, exceptions etc.
- Evite dependências cíclicas (tangles).

### Entidades

- Modelam entidades e agregados.
- Toda entidade tem um identificador (pode ser value object ou primitivo).
- Modele comportamento ("interface reveladora de intenções"), mantendo alto encapsulamento; evite getters/setters desnecessários.
- Use `@dataclass(frozen=True)` para imutabilidade quando apropriado, ou implemente `__slots__` para performance.
- Pacote: `<dominio>/domain/<hierarquia do conceito>`
- Nome: nome da entidade. Ex.: `Curriculo`.

### Domain Service

Encapsula ação/operação de domínio que não cabe em entidade/agregado (interação entre agregados distintos, acesso a repositório/gateway como parte da regra, polimorfismo, passos reutilizáveis entre Services).

- Stateless.
- Normalmente 1 único método público.
- **Não crie interface + implementação por padrão**. Em Python, use classes concretas diretamente. Só crie interface quando:
  1. É um `port` (implementação fora do hexágono).
  2. Há polimorfismo (strategy, decorator, proxy etc.).
- Caso contrário, crie apenas a classe concreta.

Implementação simples (sem interface):
- Pacote: `<dominio>/domain/<hierarquia do conceito>`
- Nome: verbo no infinitivo, sufixo `Service` opcional. Ex.: `CancelarPedidoCompraService`.

Port and Adapter com implementação em `adapters` (serviços externos):
- Interface: `<dominio>/domain/<hierarquia>`. Ex.: `ConsultarTabelaSinapiService`.
- Client: `<dominio>/adapters/<funcionalidade>`. Nome: interface + sufixo `Client`. Ex.: `ConsultarTabelaSinapiServiceClient`.

### Repository

Persistência e recuperação de entidades/raízes de agregado. Diferente de DAO:
1. Representa coleção de agregados, não tabela.
2. Métodos de consulta sempre retornam o agregado **completo**.
3. Limite a quantidade de métodos; projete para necessidades comuns. Para flexibilidade use Specification/Builder (**sem** referências a SQL/banco).

Em Services `command`, **sempre** carregue entidades via repository (garantia de invariantes).

Quase todo repository é `port`: **interface em `domain`, implementação em `adapters`**.

Interface:
- Pacote: `<dominio>/domain/<hierarquia do conceito>`
- Nome: nome do agregado + sufixo `Repository`. Ex.: `OrcamentoEmpresarialRepository`.

### Validator de domínio

Use quando a invariante:
1. É complexa (ferir SRP se ficar na entidade).
2. Envolve mais de um agregado.
3. Precisa consultar dados externos (repositórios, services, configurações).

Comportamento padrão ao detectar inválido: lançar exceção de domínio. Também aceita notification pattern (acumular erros) quando não se deve interromper o fluxo.

- Pacote: `<dominio>/domain/<hierarquia do conceito>`
- Nome: nome da regra/entidade/conceito + sufixo `Validator`. Ex.: `OrcamentoEmpresarialValidator`.

## Camada: adapters

Mecanismos técnicos (web, persistência, agendamento, arquivos, integrações). Contém adapters do ports and adapters.

### Repository (implementação)

- Pacote: `<dominio>/adapters`
- Nome: nome da interface + sufixo `Impl`. Ex.: `OrcamentoEmpresarialRepositoryImpl`.

### Query (implementação)

- Pacote: `<dominio>/adapters`
- Nome: nome da Query + sufixo `Impl`. Ex.: `ConsultarVersaoOrcamentoEmpresarialQueryImpl`.

## Fontes

- Percival, H. & Gregory, B. — Architecture Patterns with Python (Cosmic Python), https://www.cosmicpython.com/book/preface.html
- Vernon, V. — Implementing Domain-Driven Design, cap. 2 (Bounded Contexts)
- Cockburn, A. — Hexagonal Architecture (conceito original, sem prescrição de pastas), https://alistair.cockburn.us/hexagonal-architecture

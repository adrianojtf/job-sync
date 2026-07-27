---
trigger: always_on
description: Padrões de design de código (baseados em Arquitetura Hexagonal + DDD)
globs:
---

# Padrões de Design de Código

Regras obrigatórias de camadas, pacotes e nomenclatura para o projeto job-sync. Baseado em Arquitetura Hexagonal e DDD adaptado para Python.

## Fundamentos

- Raiz: `src/` contém todo o código fonte da aplicação.
- Sob `src/` **só são permitidos** 4 pacotes de camada: `domain`, `application`, `infrastructure`, `ui`.
- "Dentro do hexágono" = `domain` + `application`. "Fora" = `infrastructure`.
- Direção de dependências:
  - `application` → `domain` permitido. `domain` → `application` **proibido**.
  - `infrastructure` → `domain`/`application` permitido (implementando `ports`).
  - `domain`/`application` → `infrastructure` **proibido**. Use ports and adapters: interface (`port`) dentro do hexágono, implementação (`adapter`) fora.
- Classes dentro do hexágono podem depender de bibliotecas Python padrão e libs de domínio puro, **sem** depender de infraestrutura (IO, DB, HTTP, LLM).
- Dentro do hexágono use apenas linguagem ubíqua; sem termos técnicos de infraestrutura.

## Camada: application

Aplicação/casos de uso. Tipos de classe aceitos: `UseCase`, DTOs de input/output/filter, `Validator` (de input), `Query`, exceptions específicas.

### UseCase

- Cada funcionalidade geralmente tem um UseCase correspondente; a UI delega para ele.
- **Não criar interface + implementação por padrão**. Em Python, use classes concretas diretamente. Só crie interface quando necessário para testes (mocking) ou polimorfismo.
- Método público preferencial: `executar`.
- Um UseCase **nunca** pode importar/usar outro UseCase. Se surgir essa necessidade, extraia um domain service compartilhado.
- Use injeção de dependência via construtor (`__init__`).

Implementação:
- Pacote: `application.use_cases.<conceito de domínio + funcionalidade>`
- Nome: PascalCase. Ex.: `AdaptarCurriculoParaVaga`.

Organização por funcionalidade (classes fortemente relacionadas do caso de uso ficam juntas). Ex.:

Pacote: `application.use_cases.adaptar_curriculo_para_vaga`
- `use_case.py` - `AdaptarCurriculoParaVaga`
- `dtos.py` - `AdaptarCurriculoParaVagaInputDto`, `AdaptarCurriculoParaVagaOutputDto`
- `validator.py` - `AdaptarCurriculoParaVagaInputValidator`
- `__init__.py` - Exporta as classes públicas

### DTO de UseCase

Criar apenas quando necessário. Primitivos, PKs, datas, entidades podem ser usados direto como input/output.

- Use `@dataclass(frozen=True)` para DTOs imutáveis ou `pydantic.BaseModel` para validação automática.
- Sufixos: `InputDto`, `OutputDto`, `Filter`.

1) DTO usado por um único UseCase: nome do caso de uso + sufixo. No mesmo pacote do UseCase.
  - `AdaptarCurriculoParaVagaInputDto`, `AdaptarCurriculoParaVagaOutputDto`.

2) DTO reutilizado entre UseCases do mesmo conceito: nome da entidade/conceito + sufixo. No pacote que agrupa os UseCases.
  - `CurriculoInputDto`, `CurriculoOutputDto`.

3) Estrutura em árvore: nome da entidade/conceito + sufixo.
  - `CriarTituloInputDto`, `CriarParcelaInputDto`.

UI **nunca** mapeia entidades diretamente para JSON; sempre converte para DTO.

### Query (interface)

UseCases se dividem em `command` (alteram estado) e `query` (consultam). Em `command`, sempre use `Repository`. Em `query`, se o repositório não servir (paginação, filtros variados, relatórios, agregações específicas), crie uma `Query`.

- Interface em `application.use_case`, implementação concreta em `infrastructure` (ports and adapters).
- Específica para 1 UseCase; fica no mesmo pacote do UseCase.
- 1 único método público: `execute`, recebendo filtros e retornando dados.
- Um UseCase pode chamar mais de uma `Query`, mas cada `Query` = 1 única consulta.
- Pode retornar entidades de domínio ou estruturas ad-hoc.

Localização:
- Pacote: `application.use_cases.<pacote do caso de uso que usa a query>`
- Nome: verbo no infinitivo + sufixo `Query`. Ex.: `ConsultarVersaoOrcamentoEmpresarialQuery`.

### Validator de UseCase

Validações básicas de input (obrigatoriedade, formato, existência de chave). Invariantes de negócio devem ficar no domínio, não aqui.

- Pacote: `application.use_cases.<pacote do caso de uso>`
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
- Pacote: `domain.<hierarquia do conceito>`
- Nome: nome da entidade. Ex.: `Curriculo`.

### Domain Service

Encapsula ação/operação de domínio que não cabe em entidade/agregado (interação entre agregados distintos, acesso a repositório/gateway como parte da regra, polimorfismo, passos reutilizáveis entre UseCases).

- Stateless.
- Normalmente 1 único método público.
- **Não crie interface + implementação por padrão**. Em Python, use classes concretas diretamente. Só crie interface quando:
  1. É um `port` (implementação fora do hexágono).
  2. Há polimorfismo (strategy, decorator, proxy etc.).
- Caso contrário, crie apenas a classe concreta.

Implementação simples (sem interface):
- Pacote: `domain.<hierarquia do conceito>`
- Nome: verbo no infinitivo, sufixo `Service` opcional. Ex.: `CancelarPedidoCompraService`.

Port and Adapter com implementação em `infrastructure` (serviços externos):
- Interface: `domain.<hierarquia>`. Ex.: `ConsultarTabelaSinapiService`.
- Client: `infrastructure.<funcionalidade>`. Nome: interface + sufixo `Client`. Ex.: `ConsultarTabelaSinapiServiceClient`.

### Repository

Persistência e recuperação de entidades/raízes de agregado. Diferente de DAO:
1. Representa coleção de agregados, não tabela.
2. Métodos de consulta sempre retornam o agregado **completo**.
3. Limite a quantidade de métodos; projete para necessidades comuns. Para flexibilidade use Specification/Builder (**sem** referências a SQL/banco).

Em UseCases `command`, **sempre** carregue entidades via repository (garantia de invariantes).

Quase todo repository é `port`: **interface em `domain`, implementação em `infrastructure`**.

Interface:
- Pacote: `domain.<hierarquia do conceito>`
- Nome: nome do agregado + sufixo `Repository`. Ex.: `OrcamentoEmpresarialRepository`.

### Validator de domínio

Use quando a invariante:
1. É complexa (ferir SRP se ficar na entidade).
2. Envolve mais de um agregado.
3. Precisa consultar dados externos (repositórios, services, configurações).

Comportamento padrão ao detectar inválido: lançar exceção de domínio. Também aceita notification pattern (acumular erros) quando não se deve interromper o fluxo.

- Pacote: `domain.<hierarquia do conceito>`
- Nome: nome da regra/entidade/conceito + sufixo `Validator`. Ex.: `OrcamentoEmpresarialValidator`.

## Camada: infrastructure

Mecanismos técnicos (web, persistência, agendamento, arquivos, integrações). Contém adapters do ports and adapters.

### Repository (implementação)

- Pacote: `infrastructure.<funcionalidade>`
- Nome: nome da interface + sufixo `Impl`. Ex.: `OrcamentoEmpresarialRepositoryImpl`.

### Query (implementação)

- Pacote: `infrastructure.<funcionalidade>`
- Nome: nome da Query + sufixo `Impl`. Ex.: `ConsultarVersaoOrcamentoEmpresarialQueryImpl`.

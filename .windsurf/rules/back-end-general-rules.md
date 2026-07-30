---
trigger: always_on
description: Regras gerais de desenvolvimento compartilhadas entre todos os projetos back-end Python
globs:
---

# Regras para APIs REST

## Organização e consistência
- Quando for criar routers/endpoints, verifique outros routers do projeto para utilizar os mesmos padrões de organização e decoradores (FastAPI).
- Só altere o contrato de APIs Rest (path/URL, retorno de erros, estrutura de dados, etc.), quando isso for explicitamente solicitado.
- Mantenha consistência nos nomes de endpoints e parâmetros com a linguagem ubíqua do domínio.
- Use Pydantic models para validação de input/output e documentação automática.

## Modelagem de recursos (Richardson Maturity Model, nível 2)
- URLs identificam recursos (substantivos), nunca ações (verbos).
  Correto: `POST /candidaturas`. Incorreto: `POST /criar-candidatura`.
- Use substantivos no plural para coleções: `/curriculos`, `/candidaturas`.
- Hierarquia de recursos reflete relação de posse real, não navegação de UI:
  `/curriculos/{id}/secoes` (uma seção só existe dentro de um currículo).
  Se o recurso tem identidade própria fora dessa relação, use um recurso
  de nível superior com filtro: `/candidaturas?curriculo_id={id}`.
- Verbos HTTP mapeiam a operação, o path nunca repete o verbo:
  - GET     -> leitura (idempotente, sem efeito colateral)
  - POST    -> criação de recurso novo, ou ação que não é CRUD puro
  - PUT     -> substituição completa do recurso (idempotente)
  - PATCH   -> atualização parcial (idempotente na intenção, não no efeito)
  - DELETE  -> remoção (idempotente: chamar duas vezes tem o mesmo resultado)
- Ações que não são CRUD (ex: "tailorizar currículo") viram sub-recurso ou
  verbo de domínio explícito, não parâmetro escondido:
  `POST /candidaturas/{id}/tailoring` é preferível a
  `POST /candidaturas/{id}?action=tailor`.

## Status codes
- Use o código HTTP mais específico disponível, não genérico por padrão:
  - 200 OK -> sucesso com corpo de resposta
  - 201 Created -> recurso criado, incluir header `Location` com a URL do novo recurso
  - 202 Accepted -> processamento assíncrono aceito, ainda não concluído
  - 204 No Content -> sucesso sem corpo (ex: DELETE)
  - 400 Bad Request -> erro de validação do cliente
  - 404 Not Found -> recurso não existe
  - 409 Conflict -> conflito de estado (ex: recurso já existe, versão desatualizada)
  - 422 Unprocessable Entity -> sintaticamente válido, semanticamente inválido
    (FastAPI já usa este código por padrão em erros de Pydantic)
  - 500 Internal Server Error -> nunca expor stack trace ou detalhe interno no corpo
- Nunca retornar 200 com um corpo indicando erro (`{"success": false}`).
  O status code é o contrato, não o corpo.

## Formato de erro consistente
- Padronizar um único formato de erro em todo o projeto (ex: RFC 7807
  Problem Details), aplicado por um exception handler central, não
  tratado individualmente em cada endpoint:
```json
  {
    "type": "https://projeto.com/erros/curriculo-nao-encontrado",
    "title": "Currículo não encontrado",
    "status": 404,
    "detail": "Nenhum currículo com id 'abc-123' foi encontrado.",
    "instance": "/curriculos/abc-123"
  }
```
- Verificar se já existe um exception handler central no projeto antes
  de criar tratamento de erro local em um endpoint novo.

## Versionamento
- Versionar a API de forma explícita e visível (`/v1/curriculos`), nunca
  depender de versionamento implícito por header custom sem documentação.
- Mudança que quebra contrato exige nova versão, não alteração silenciosa
  da versão atual (reforça a regra acima: contrato só muda se solicitado).

## Paginação, filtros e ordenação em coleções
- Toda rota que retorna coleção potencialmente grande deve suportar
  paginação desde o início, não como retrofit:
  `GET /candidaturas?limit=20&offset=0` ou paginação por cursor,
  seguindo o que já existir no projeto.
- Resposta paginada inclui metadados de contagem, não só os itens:
```json
  {
    "items": [...],
    "total": 134,
    "limit": 20,
    "offset": 0
  }
```
- Filtros e ordenação via query params (`?status=enviada&sort=-created_at`),
  nunca via corpo em métodos GET.

## HATEOAS (quando o projeto exigir nível 3 de maturidade REST)
- Aplicar HATEOAS apenas se o projeto explicitamente adotar esse padrão
  (verificar se já existe precedente no projeto antes de introduzir).
  Não é a prática mais comum em APIs internas ou de baixo acoplamento
  cliente-servidor — avaliar custo/benefício antes de aplicar por padrão.
- Quando aplicado, cada recurso retorna um bloco `_links` com as ações
  disponíveis a partir do estado atual do recurso, e não com todas as
  ações teoricamente possíveis:
```json
  {
    "id": "abc-123",
    "status": "rascunho",
    "_links": {
      "self": { "href": "/candidaturas/abc-123" },
      "submeter": { "href": "/candidaturas/abc-123/submissao", "method": "POST" },
      "curriculo": { "href": "/curriculos/xyz-789" }
    }
  }
```
- O cliente deve navegar pelos links retornados em vez de montar URLs
  a partir de conhecimento fixo da API — esse é o critério real que
  diferencia HATEOAS de um simples campo de metadados.
- Se o time/cliente da API não consome os links dinamicamente, HATEOAS
  não está de fato sendo praticado, apenas simulado — sinal para
  reavaliar se vale manter a complexidade.

## Segurança e boas práticas gerais
- Nunca expor identificadores internos sequenciais (`/curriculos/1`) em
  API pública; preferir UUID.
- Autenticação e autorização são cross-cutting concerns: implementar via
  dependency injection do FastAPI (`Depends`), nunca duplicar checagem
  manual em cada endpoint.
- Rate limiting e CORS configurados de forma centralizada, não por rota.

# Regras específicas de FastAPI

## Estrutura e organização de routers
- Um router por recurso/domínio (`curriculo_router.py`, `candidatura_router.py`),
  registrado com `APIRouter(prefix=..., tags=...)`, nunca todos os
  endpoints em um único `main.py`.
- `tags` do router deve corresponder ao nome do recurso, garantindo que
  a documentação gerada agrupe endpoints de forma coerente.
- Path operations (`@router.get`, `@router.post`, etc.) sempre com
  `response_model` explícito — nunca depender de inferência implícita
  de tipo de retorno para o schema de resposta.
- Use `status_code` explícito no decorator quando diferente do padrão
  200 (ex: `@router.post(..., status_code=201)`), não confiar no default.

## Dependency Injection
- Regras de negócio, acesso a repositório e chamadas a serviços externos
  nunca ficam direto no corpo da path operation — a função do endpoint
  orquestra, delega para a camada de aplicação (use case/service).
- Dependências compartilhadas (sessão de banco, autenticação, use cases)
  via `Depends`, centralizadas em um módulo de dependências
  (`dependencies.py`), não recriadas em cada router.
- Preferir `Annotated[Tipo, Depends(...)]` (padrão recomendado pelo
  FastAPI desde a versão 0.95) em vez de `Depends()` direto como default
  de parâmetro, para manter compatibilidade com reuso de tipos.

## Validação e schemas Pydantic
- Nunca usar a mesma entidade de domínio como `response_model` da API.
  Sempre um Pydantic model de schema (`CurriculoResponse`,
  `CurriculoCreateRequest`) que traduz de/para a entidade — evita
  vazamento de detalhes internos do domínio no contrato HTTP.
- Separar schema de entrada (`*Request`/`*Create`/`*Update`) do schema
  de saída (`*Response`), mesmo que pareçam idênticos hoje — eles
  evoluem em direções diferentes.
- Validações de formato (regex, min/max length, tipos) ficam no Pydantic
  model; validações de regra de negócio (ex: "currículo não pode ter
  seção duplicada") ficam no domínio, nunca replicadas no schema.
- Usar `Field(..., description="...")` em todos os campos de schemas
  expostos publicamente, pois isso alimenta diretamente a documentação
  OpenAPI gerada.

## Assincronismo
- Path operations que chamam I/O (banco, API externa, arquivo) devem
  ser `async def`, com o adapter correspondente também assíncrono
  (ex: cliente HTTP assíncrono para chamadas ao Groq).
- Nunca misturar chamada síncrona bloqueante dentro de `async def` sem
  `run_in_threadpool` ou equivalente — isso trava o event loop.
- Se o adapter usado (ex: SDK de terceiro) só existir em versão síncrona,
  isolar a chamada e usar `run_in_threadpool`, deixando explícito no
  código o motivo.

# Documentação da API

## OpenAPI/Swagger (gerado automaticamente pelo FastAPI)
- Toda path operation deve ter `summary` e, quando o comportamento não
  for óbvio pelo nome, `description` — o FastAPI expõe isso direto na
  documentação interativa (`/docs`), sem custo extra.
- Usar `docstring` na função do endpoint como fonte da descrição longa
  quando a lógica tiver nuances (ex: efeitos colaterais, restrições de
  estado) — o FastAPI já injeta a docstring na documentação.
- Todo `response_model` deve ter exemplos via `json_schema_extra` ou
  `Field(examples=[...])` nos campos, para que `/docs` mostre payload
  realista, não apenas tipos.
- Documentar todos os status codes de erro possíveis por endpoint via
  `responses={404: {"model": ErrorSchema, "description": "..."}}`,
  não deixar implícito apenas o 200/201 de sucesso.
- Manter `title`, `version` e `description` do `FastAPI(...)` no
  `main.py` atualizados e coerentes com o versionamento real da API.

## Documentação complementar ao código
- Decisões de arquitetura que não são óbvias pelo código (ex: por que
  um endpoint é assíncrono, por que um recurso foi modelado de certa
  forma) vão em ADR (Architecture Decision Record) ou comentário
  próximo ao código, não apenas na cabeça de quem escreveu.
- Contratos de API não documentados no OpenAPI (ex: webhooks, eventos)
  precisam de documentação manual equivalente — não assumir que
  "está no código" é suficiente para quem consome a API.

# Arquitetura

Nota: esta seção reflete uma decisão de projeto (Hexagonal Architecture
+ DDD), não uma prescrição do FastAPI, que é agnóstico de arquitetura.

## Separação de camadas
- FastAPI (routers, dependencies, schemas Pydantic) vive inteiramente na
  camada de infraestrutura/entrypoints — nunca a camada de domínio ou
  service_layer importa algo de `fastapi` ou `pydantic` para regra de
  negócio.
- Path operation é um adapter de entrada: ela traduz request HTTP em
  chamada de caso de uso, e resultado de caso de uso em response HTTP.
  Não deve conter lógica de negócio.
- Ao adicionar um domínio novo (seguindo o padrão de múltiplos domínios
  já registrado: `<dominio>/domain`, `<dominio>/service_layer`,
  `<dominio>/adapters`), o router correspondente fica em `entrypoints/`,
  nomeado de forma consistente com o domínio (`candidatura_router.py`
  para o domínio `candidatura`).

## Regra de dependência entre domínios via API
- Um endpoint de um domínio pode depender do service_layer de outro
  domínio (ex: endpoint de `candidatura` usando `curriculo_repo` para
  buscar dados), mas nunca importa diretamente o router de outro
  domínio — a composição acontece via injeção de dependência, não via
  chamada HTTP interna entre routers do mesmo processo.
- Casos de uso que cruzam domínios (ex: tailoring) são expostos por um
  único endpoint no domínio "dono do resultado", replicando a regra já
  definida na camada de aplicação — não criar endpoint próprio de
  "orquestração" fora dos domínios existentes.

## Composition root
- Instanciação de adapters concretos (cliente Groq, conexão de banco,
  repositórios) acontece em um módulo único de composição
  (`dependencies.py` ou `composition_root.py`), injetado via `Depends`
  nos routers — nunca instanciado direto dentro da função do endpoint.
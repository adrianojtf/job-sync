---
name: functional-tests-db-exploration
description: Gerar guia de testes funcionais de um endpoint REST cruzando regras do código com dados reais via MCP do PostgreSQL, produzindo requisições Postman prontas para comparar banco x resposta da API
argument-hint: "[caminho do Controller ou endpoint]"
allowed-tools:
  - read
  - grep
  - glob
  - mcp-postgres
triggers:
  - user
  - model
---

# Testes Funcionais orientados a dados reais (MCP PostgreSQL)

Gera um documento `.md` que serve de roteiro de teste funcional para um endpoint REST:
replica as regras de negócio do código, usa o MCP do PostgreSQL para achar/derivar dados
reais que cobrem cada regra, e entrega uma lista de requisições Postman com o resultado
esperado de cada uma — para comparação manual banco x resposta da API.

## Quando usar

- Validar se a implementação **atual** (branch/master) de um endpoint está de acordo com
  as regras de negócio, sem depender de massa de teste fabricada manualmente.
- Antes de um code review de MR que altera regra de negócio de uma consulta/validação.
- Como insumo para o revisor/QA comparar banco x resposta sem reimplementar a lógica.

Não usar para gerar testes unitários (JUnit) — isso é código, não documento de teste
funcional. Não usar para popular/alterar dados no banco (o MCP deve ser usado **somente
leitura**).

## Processo

### 1. Delimitar o escopo

Peça/identifique explicitamente:
- **Endpoint** (Controller + método) a testar. Ex.: `KeyHandoverController.consultar`.
- Pasta de destino do documento, seguindo o padrão de `sdd/specs/<dominio>/<subdominio>/<feature>/<historia>/`.
  Procure a pasta da história (por chave Jira ou nome da feature) e olhe os arquivos irmãos
  (`adr-*.md`, `analise-*.md`, `techspec-*.md`) para manter o mesmo diretório. Se não achar
  a pasta, pergunte ao usuário em vez de adivinhar.
- Nome do arquivo: `testes-funcionais-<recurso-em-kebab-case>.md` (ex.: `testes-funcionais-get-key-handovers.md`).

#### 1.1 Verificar se o Controller/endpoint já existe

Antes de mapear regras, confirme via `grep_search`/`code_search` se o Controller e o método
HTTP alvo **já existem** na branch atual (endpoint pode estar previsto em UseCase/Query mas
ainda sem exposição REST, como ocorre entre histórias que dividem UseCase e Controller).

- Se o Controller **existir**: siga normalmente para a seção 2.
- Se o Controller **não existir** (ou existir mas faltar o método do endpoint): **pergunte
  explicitamente ao usuário** se deseja que você gere o Controller e os demais arquivos
  necessários (DTOs de request/response, wiring no `*Module` Spring, etc.) apenas para
  viabilizar a execução dos testes funcionais no Postman. Não gere esses arquivos sem
  confirmação explícita — isso é implementação de código, fora do escopo padrão desta skill.
  - Se confirmado, siga os padrões de `code-design-standards` (Controller em
    `infrastructure.web.api.<funcionalidade>.v1`, DTOs no mesmo pacote, delegando para o
    UseCase já existente) e as regras de `back-end-general-rules` (reaproveitar anotações e
    organização de outros Controllers do módulo, não alterar contrato de APIs existentes).
  - Se o usuário recusar, gere o documento e a coleção Postman mesmo assim, mas registre
    explicitamente no documento (e na coleção) que o endpoint ainda não existe na branch e
    que as requisições servem para quando ele for implementado.

### 2. Mapear as regras no código (sem ler o projeto inteiro)

Use `code_search`/`grep_search` a partir do Controller para encontrar, na ordem:
1. **Controller** → método HTTP, path, request/query params, DTO de entrada/saída.
2. **UseCase** (`execute`) → validações de input (`Validator`), mensagens de erro e HTTP status.
3. **Query/Repository** → filtros aplicados (equivalência campo do filtro ↔ coluna/tabela SQL),
   joins, `EXISTS`/subqueries, ordenação (ou ausência dela — ver seção 4).
4. **Domain Service/Validator** → regras que decidem o resultado exibido (ex.: elegibilidade,
   status calculado, mensagens), reproduza a lógica como uma **tabela de decisão** (condição → resultado),
   igual a uma tabela de verdade. Anote a ordem de avaliação quando a lógica **interrompe** no
   primeiro caso verdadeiro (isso é essencial para prever o resultado certo).
5. Se alguma regra depende de lógica legada complexa não trivial de reproduzir em SQL
   (ex.: bloqueio contábil, factories antigas), **não tente simular por aproximação silenciosa**:
   documente como suposição explícita ("assumimos X não está bloqueado no ambiente") para que
   divergências nesse ponto não sejam confundidas com bug do código sob teste.

Evite abrir arquivos inteiros; leia só os métodos relevantes (`grep_search` com `MatchPerLine`
ou leitura por range de linhas).

### 3. Explorar o banco com o MCP do PostgreSQL (leitura, econômica)

Use apenas ferramentas de leitura (`mcp4_execute_sql` só com `SELECT`, `mcp4_get_object_details`,
`mcp4_list_objects`). Nunca gere `INSERT`/`UPDATE`/`DELETE`.

Para economizar tokens, siga esta ordem de queries (reaproveite os templates, não gere queries
ad hoc soltas linha a linha):

1. **Query de descoberta agregada** — encontrar candidatos que satisfaçam a massa de filtros
   principais (ex.: empresa/centro de custo com maior volume do registro-alvo), com `GROUP BY`
   e `ORDER BY ... DESC LIMIT N`. Objetivo: achar rapidamente um ambiente (empresa/filial/cliente)
   com dados suficientes, sem trazer linha a linha.
2. **Query de listagem enxuta** — `SELECT DISTINCT` só das colunas necessárias para montar a
   tabela de massa de dados (poucas dezenas de linhas, com `LIMIT`).
3. **Query de avaliação agregada da regra** — traduza a tabela de decisão do passo 2 em UMA
   query com `bool_or`/`EXISTS`/`CASE` que devolve, por registro candidato, os flags booleanos
   de cada condição da regra. Isso evita ficar avaliando registro por registro "na cabeça"
   (gasta menos tokens que trazer dados brutos e re-derivar a lógica no contexto do modelo).
4. **Query de detalhe** — só para os poucos candidatos escolhidos (idealmente 1 por cenário),
   busque o detalhe fino (ex.: por parcela/item) necessário para confirmar qual condição
   dispara primeiro quando há ordem de interrupção.

Regras de economia:
- Nunca faça `SELECT *` em tabela grande sem `LIMIT`.
- Prefira 1 (no máximo 2) exemplo real por ramo de regra — não enumere todas as ocorrências.
- Empurre lógica para o SQL (`bool_or`, `EXISTS`, `CASE`) em vez de trazer linhas cruas para
  interpretar manualmente.
- Reutilize os mesmos filtros-base (empresa/centro de custo/cliente) entre as queries dos
  passos 2-4 para não precisar re-explorar o esquema a cada cenário.

### 4. Ordenação não determinística

Se a query do passo 2 da seção 2 não tiver `ORDER BY` explícito e a regra de negócio
**interrompe no primeiro match**, documente isso como uma observação de risco explícita no
documento final (a resposta real pode variar entre execuções). Não finja que existe uma ordem
garantida.

### 5. Gerar o documento

Estruture o `.md` seguindo este esqueleto (mesmas seções de
`sdd/specs/financeiro/contas-a-receber/entrega-de-chaves/sitx-2562-api-entrega-de-chaves/testes-funcionais-get-key-handovers.md`):

```markdown
# Testes Funcionais — `<METODO> <path>`

**Objetivo:** validar, comparando banco de dados x resposta do endpoint, o comportamento
atual (código na branch) de `<Controller.metodo>` (`@<path-do-controller>:<linha>`).

**Ambiente consultado:** banco `<nome>` (MCP PostgreSQL local), <observação sobre dados usados>.

> Notas de contexto relevantes (ex.: divergência com techspec, escopo reduzido, etc.).

---

## 1. Regras replicadas do código
### 1.1 Validações do use case
| Regra | Mensagem | HTTP |
### 1.2 Filtros aplicados na query
(lista campo do filtro ↔ tabela.coluna real)
### 1.3 Regra de decisão / elegibilidade
(passos numerados, ordem de avaliação, o que interrompe)
**Observações** (bloqueio legado não simulável, ordenação não determinística, etc.)

## 2. Massa de dados encontrada (<contexto: empresa/centro de custo/cliente>)
Tabela com os registros candidatos e seus atributos-chave.
### 2.1 Avaliação de <regra> por registro (agregada via SQL, ver seção 4)
Tabela: id | flags da regra | resultado esperado | mensagem/status esperado

## 3. Requisições sugeridas (Postman)
Uma subseção por cenário, cobrindo no mínimo:
- Um cenário por ramo distinto da regra de decisão (happy path + cada bloqueio).
- Um cenário de resultado vazio (filtro que não bate com nada).
- Um cenário por combinação de parâmetro obrigatório ausente (erros 4xx).
- Cenários de paginação/ordenação, se o endpoint suportar.
Cada cenário: request (`GET {{baseUrl}}/...`) + resultado esperado (campos e valores).

## 4. Queries SQL usadas na exploração (para reconferir / repetir com outro contexto)
Bloco `sql` com as queries reais executadas (descoberta, listagem, avaliação agregada, detalhe).

## 5. Roteiro de comparação sugerido
Passo a passo de que campos comparar, o que fazer com divergência, e quais observações da
seção 1 não devem ser confundidas com bug.
```

### 6. Salvar e revisar

- Salve com `write_to_file` no caminho definido no passo 1.
- Releia a tabela de decisão do passo 2 contra as requisições geradas: cada linha da tabela
  de decisão deve ter pelo menos um cenário Postman correspondente.
- Não implemente código nem altere o endpoint — este é um artefato de documentação/QA
  (exceto pelos arquivos de Controller eventualmente gerados no passo 1.1, com confirmação
  explícita do usuário).

### 7. Gerar a coleção Postman executável

Além do `.md`, gere um arquivo de **coleção Postman** (`Postman Collection Format v2.1`) na
mesma pasta do documento, contendo todas as requisições da seção 3 já com os dados reais
obtidos no passo 3 (sem placeholders de dados a preencher manualmente — apenas `{{baseUrl}}`
como variável de ambiente).

- Nome do arquivo: `postman-testes-funcionais-<recurso-em-kebab-case>.json` (mesmo
  `<recurso>` usado no `.md`), salvo na mesma pasta.
- Estrutura mínima do JSON:
  - `info.name` = mesmo título do `.md` (ex.: `Testes Funcionais - GET /v1/key-handovers`).
  - `variable`: pelo menos `baseUrl` (ex.: `http://localhost:9090`).
  - Uma **pasta** (`item` com `item[]` aninhado) por seção de cenário (happy path, cada
    bloqueio/ramo da regra, vazio, validações 4xx, paginação), espelhando a seção 3 do `.md`.
  - Cada requisição usa `request.url.raw` com os mesmos query params/valores reais do `.md`
    (não inventar novos IDs).
  - Cada requisição inclui um `event` do tipo `test` (`exec` em Javascript, usando `pm.test`)
    que verifica automaticamente o essencial do resultado esperado documentado na seção 3:
    - status code esperado (`200`, `422`, etc.);
    - para respostas de sucesso, pelo menos: contagem (`resultSetMetadata.count` ou tamanho
      de `results`) e, quando aplicável, `deletable`/`statusDescription` (ou campo
      equivalente) do primeiro registro relevante;
    - para respostas de erro, a mensagem exata esperada.
  - Não usar `pm.test` genérico ("deve retornar 200") sem checar o conteúdo relevante — o
    objetivo é que a execução da coleção já sinalize divergência automaticamente.
- Se o passo 1.1 identificou que o Controller ainda não existe e o usuário optou por **não**
  gerá-lo, gere a coleção do mesmo jeito (ela servirá de contrato para quando o endpoint for
  implementado), mas adicione um `description` na raiz da coleção avisando que os testes
  falharão até o endpoint existir.
- Não inclua nenhuma requisição de escrita (POST/PUT/PATCH/DELETE) que altere estado do banco,
  a menos que o cenário testado seja explicitamente sobre esse método e o `.md` já documente
  a regra correspondente.

## Checklist

- [ ] Verificado se o Controller/endpoint já existe; se não, perguntado ao usuário antes de gerar Controller/DTOs/wiring
- [ ] Controller, UseCase, Query e regra de domínio identificados via leitura direcionada (não o projeto inteiro)
- [ ] Tabela de decisão da regra de negócio replicada com ordem de avaliação explícita
- [ ] Suposições sobre lógica legada não simulável documentadas como tal
- [ ] Queries de exploração usam agregação/`LIMIT`/flags booleanos em SQL, não dump de linhas
- [ ] 1 exemplo real por ramo de regra (não todas as ocorrências)
- [ ] Observação sobre ordenação não determinística incluída quando aplicável
- [ ] Documento salvo na mesma pasta `sdd/specs/.../<historia>/` dos demais artefatos da história, com nome `testes-funcionais-<recurso>.md`
- [ ] Cada cenário Postman tem resultado esperado explícito (campos + valores, não só "ok")
- [ ] Cenários cobrem: happy path, cada bloqueio/ramo da regra, vazio, validações 4xx, paginação/ordenação (se houver)
- [ ] Nenhuma query de escrita (`INSERT`/`UPDATE`/`DELETE`) foi executada no banco
- [ ] Coleção Postman (`postman-testes-funcionais-<recurso>.json`) gerada na mesma pasta, com dados reais e `pm.test` verificando status + conteúdo esperado de cada cenário

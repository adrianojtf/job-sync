# Especificação Técnica — JOB-0038

PRD de referência: `prd-job-0038.md` (mesmo diretório).

## Resumo Executivo

O board passa a usar `@dnd-kit` (core, sortable e utilities) para arrastar e soltar com mouse, toque e teclado. O título do cartão vira um botão que abre o `DetalheCandidaturaModal` existente, e a caixa de seleção "Mover para" é removida. O layout muda de grade de 4 colunas para colunas de largura fixa em uma área com rolagem horizontal, com rolagem vertical por coluna.

Para guardar a ordem dos cartões, o backend ganha o campo `posicao` na candidatura. A regra de reordenação fica numa função pura do domínio. O caso de uso `MoverCandidatura` recebe uma `posicao` opcional e persiste a coluna de destino inteira em uma transação. O endpoint `POST /v1/candidaturas/{id}/submissao` ganha o campo opcional `posicao`, sem quebrar quem já o chama. No frontend, a mutation de mover faz atualização otimista com retorno ao estado anterior em caso de erro.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Backend (`src/jobsync`):

| Componente | Situação | Responsabilidade |
|---|---|---|
| `candidatura/domain/candidatura.py` | **Modificado** | Campo `posicao: int` (>= 0). `Candidatura.nova` recebe `posicao=0` |
| `candidatura/domain/ordenacao_coluna.py` | **Novo** | Função pura `reposicionar(ids, movido_id, posicao)` que devolve a nova ordem da coluna |
| `candidatura/domain/candidatura_repository.py` | **Modificado** | Novos métodos `buscar_por_id` e `aplicar_movimento` (porta) |
| `candidatura/adapters/candidatura_repository_impl.py` | **Modificado** | Coluna `posicao`, `ORDER BY posicao`, `aplicar_movimento` transacional, `salvar` insere no topo |
| `shared_kernel/adapters/persistence/_conexao_sqlite.py` | **Modificado** | Migração leve: adiciona `posicao` e preenche as linhas antigas |
| `candidatura/service_layer/mover_candidatura/service.py` | **Modificado** | `executar(id, novo_status, posicao=None)` |
| `candidatura/service_layer/listar_candidaturas_por_status/service.py` | **Sem mudança** | A ordem vem do repositório |
| `entrypoints/api/schemas/candidatura.py` | **Modificado** | `posicao` opcional em `CandidaturaSubmeterRequest`; `posicao` em `CandidaturaResponse` |
| `entrypoints/api/routers/candidatura_router.py` | **Modificado** | Repassa `posicao` ao caso de uso |
| `job-sync.postman_collection.json` | **Modificado** | Exemplo com `posicao` |

Frontend (`frontend/src`):

| Componente | Situação | Responsabilidade |
|---|---|---|
| `package.json` | **Modificado** | `@dnd-kit/core@6.3.1`, `@dnd-kit/sortable@10.0.0`, `@dnd-kit/utilities@3.2.2` (versões fixas, como o resto do projeto) |
| `api/api-client.ts`, `http-api-client.ts`, `schema.d.ts`, `tipos.ts` | **Modificado** | `moverCandidatura(id, novoStatus, posicao?)`; schema regenerado com `npm run gerar-tipos` |
| `features/candidaturas/CandidaturasPage.tsx` | **Modificado** | Monta o `DndContext`, as colunas e o `DragOverlay`; remove `select` e botão "Detalhes". Guarda só o `id` da candidatura em detalhe e a obtém do cache, para o modal refletir o status novo |
| `features/candidaturas/DetalheCandidaturaModal.tsx` | **Modificado** | Campo "Mover para" (select com os 4 status) que chama a mesma mutation, com `posicao: 0` |
| `features/candidaturas/use-mover-com-aviso.ts` | **Novo** | Hook que junta a mutation e o toast de sucesso/erro, usado pelo arrasto e pelo modal (DRY) |
| `features/candidaturas/ColunaKanban.tsx` | **Novo** | Coluna: cabeçalho, contagem, área de soltura (`useDroppable`) e `SortableContext` |
| `features/candidaturas/CartaoCandidatura.tsx` | **Novo** | Cartão ordenável (`useSortable`) com título em botão. Também exporta a versão visual usada no overlay |
| `features/candidaturas/movimento.ts` | **Novo** | Funções puras: `calcularDestino(quadro, ativoId, sobreId)` e `aplicarMovimento(quadro, ...)` (estado otimista) |
| `features/candidaturas/anuncios.ts` | **Novo** | Textos pt-BR de acessibilidade do dnd-kit |
| `features/candidaturas/use-candidaturas.ts` | **Modificado** | `useMoverCandidatura` com `onMutate`, `onError` e `onSettled` |
| `features/candidaturas/CandidaturasPage.module.css` | **Modificado** | Layout em colunas fixas, rolagem, estados de arrasto |
| `features/candidaturas/status.ts` | **Modificado** | Tom de cor por coluna (`COR_STATUS`) |
| `shared/formatacao.ts` | **Modificado** | `formatarTempoRelativo(data)` ("há 3 dias") |
| Testes (`CandidaturasPage.test.tsx`, novos `movimento.test.ts`, E2E e axe) | **Modificado/Novo** | Ver Abordagem de Testes |

Fluxo de dados:

1. O usuário pega o cartão (ponteiro, toque ou teclado). O `DragOverlay` mostra o cartão levantado.
2. Ao soltar, `calcularDestino` devolve `{status, posicao}`. Se nada mudou, nada é enviado.
3. `onMutate` cancela consultas em andamento, guarda o estado atual e grava o novo quadro no cache.
4. O cliente chama `POST /v1/candidaturas/{id}/submissao` com `novo_status` e `posicao`.
5. O backend reordena a coluna de destino (e fecha o vazio na de origem) em uma transação.
6. Em erro, `onError` restaura o cache e mostra o toast. Em qualquer caso, `onSettled` invalida a consulta.

## Design de Implementação

### Interfaces Principais

```python
# candidatura/domain/ordenacao_coluna.py
def reposicionar(ids: tuple[str, ...], movido_id: str, posicao: int | None) -> tuple[str, ...]:
    """Remove movido_id de ids (se estiver) e o insere em posicao (None = topo, limitada a [0, len])."""

# candidatura/domain/candidatura_repository.py
class CandidaturaRepository(ABC):
    def buscar_por_id(self, candidatura_id: str) -> Candidatura | None: ...
    def aplicar_movimento(
        self, candidatura_id: str, novo_status: StatusCandidatura,
        ids_destino_ordenados: tuple[str, ...],
    ) -> Candidatura: ...  # transacional; levanta CandidaturaNaoEncontrada
```

```python
# service_layer/mover_candidatura/service.py
def executar(self, candidatura_id: str, novo_status: StatusCandidatura,
             posicao: int | None = None) -> Candidatura:
    atual = self.repositorio_candidatura.buscar_por_id(candidatura_id)
    if atual is None: raise CandidaturaNaoEncontrada(candidatura_id)
    coluna = ids_da_coluna(listar_por_perfil(atual.perfil_identificador), novo_status)
    ordem = reposicionar(coluna, candidatura_id, posicao)
    return self.repositorio_candidatura.aplicar_movimento(candidatura_id, novo_status, ordem)
```

```ts
// features/candidaturas/movimento.ts
export interface Destino { status: StatusCandidatura; posicao: number }
export function calcularDestino(quadro: CandidaturasPorStatus, ativoId: string, sobreId: string): Destino | null;
export function aplicarMovimento(quadro: CandidaturasPorStatus, ativoId: string, destino: Destino): CandidaturasPorStatus;
```

`sobreId` é o id de outro cartão ou o id da coluna (`coluna:APLICADO`), quando o destino é uma coluna vazia ou o espaço abaixo dos cartões.

Sensores do `DndContext`:

- `PointerSensor` com `activationConstraint: { distance: 6 }`: o clique no título não vira arrasto (RF14).
- `TouchSensor` com `activationConstraint: { delay: 200, tolerance: 8 }`: a rolagem por toque continua funcionando (RF1, RF20).
- `KeyboardSensor` com `sortableKeyboardCoordinates` (RF17).
- `autoScroll` do dnd-kit habilitado nas áreas rolantes (RF22).
- `collisionDetection`: `closestCorners`, adequado para colunas com cartões.

Movimento pelo modal (RF18a, RF18b): o `select` do detalhe chama `mover({ id, novoStatus, posicao: 0 })`. Como usa a mesma mutation, ganha a atualização otimista e o retorno ao estado anterior. O valor do `select` vem da candidatura no cache, então volta sozinho ao status anterior em caso de erro.

O nó de ativação do arrasto por teclado é o próprio cartão (`setActivatorNodeRef`). O dnd-kit só inicia o arrasto quando o foco está nesse nó, então o título (botão interno) continua com Enter para abrir o detalhe. Esse comportamento precisa ser confirmado na primeira tarefa (ver Riscos).

### Modelos de Dados

Tabela `candidatura`: nova coluna `posicao INTEGER NOT NULL DEFAULT 0`. A posição é o índice do cartão dentro de `(perfil_identificador, status)`, começando em 0.

Migração em `criar_conexao`, executada após o `executescript` do schema:

1. Ler `PRAGMA table_info(candidatura)`. Se `posicao` não existir, executar `ALTER TABLE candidatura ADD COLUMN posicao INTEGER NOT NULL DEFAULT 0`.
2. Para cada `(perfil, status)`, numerar as linhas por `data_aplicacao DESC` (RF11). Só roda quando a coluna acabou de ser criada.

`CandidaturaResponse` ganha `posicao: int`. O tipo `Candidatura` do frontend acompanha pelo schema gerado.

### Endpoints de API

`POST /v1/candidaturas/{id}/submissao` (existente):

```json
{ "novo_status": "entrevista", "posicao": 0 }
```

- `posicao` é opcional, inteiro >= 0, índice na coluna de destino. Ausente = topo. Valor maior que o tamanho da coluna vale como "fim".
- `GET /v1/candidaturas` continua agrupado por status, com cada lista já ordenada por `posicao`.
- Erros: 404 (candidatura inexistente), 422 (status ou posição inválidos), como hoje.

Escolha: estender o endpoint existente em vez de criar um novo (KISS). A mudança é compatível, e o cliente Streamlit/Postman segue válido.

## Pontos de Integração

Não há serviço externo. O único ponto de contato é o contrato OpenAPI entre API e frontend, regenerado com `npm run gerar-tipos` (mesmo Python do CI, como no JOB-0037).

## Abordagem de Testes

Seguir TDD (red-green-refactor) e as regras em `.windsurf/rules/testing-rules.md`.

### Testes Unidade

Backend (`src/jobsync/tests/candidatura/`):

- `test_ordenacao_coluna.py`: `reposicionar` com posição no início, meio e fim, posição acima do tamanho, `None`, movido já presente (mesma coluna) e coluna vazia.
- `test_mover_candidatura_service.py`: mudança de coluna com posição, reordenação na mesma coluna, posição omitida (topo), candidatura inexistente. Usar repositório em memória/fake.
- `test_candidatura.py`: `posicao` negativa é rejeitada.
- `test_candidatura_repository_impl.py` (SQLite real em arquivo temporário): ordem por `posicao`, `aplicar_movimento` fecha o vazio da origem, transação sem estado parcial, migração de banco antigo (cria tabela sem `posicao`, abre com `criar_conexao`, confere a ordem por data).
- `entrypoints/api/test_routers.py` e `test_schemas.py`: `posicao` opcional, validação 422, `posicao` na resposta.

Frontend (Vitest + Testing Library + MSW):

- `movimento.test.ts`: `calcularDestino` e `aplicarMovimento` (entre colunas, na mesma coluna, coluna vazia, soltar sobre a própria posição = `null`).
- `CandidaturasPage.test.tsx`: título abre o detalhe; "Mover para" no detalhe move a candidatura para o topo da coluna escolhida, atualiza o status exibido no modal e restaura o valor em caso de erro; não há `select` nem botão "Detalhes"; movimento por teclado (Espaço, seta, Espaço) envia `novo_status` e `posicao` corretos; erro da API restaura o cartão e mostra o toast; anúncios em pt-BR.
- `http-api-client.test.ts`: corpo com `posicao` quando informada.
- `formatacao.test.ts`: `formatarTempoRelativo`.

O jsdom não calcula layout, então o arrasto por ponteiro não é testado ali; a cobertura dele fica no E2E.

### Testes de Serviço

Playwright (`frontend/e2e/`):

- Arrastar com o mouse (`mouse.down/move/up`) entre colunas e dentro da coluna; recarregar e conferir a persistência (RF8).
- Clique no título abre o detalhe; arrasto não abre.
- Mover pelo campo "Mover para" do detalhe e conferir a coluna do board após fechar o modal.
- Larguras 375, 768 e 1280 px: sem rolagem horizontal da página; a área do board rola; as colunas mantêm largura fixa.
- `acessibilidade.spec.ts`: axe na tela de Candidaturas com cartões e durante o arrasto por teclado.
- Emulação de toque em um viewport móvel: rolagem da página e arrasto após toque longo.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. **Domínio e persistência** (`posicao`, `reposicionar`, migração, repositório). Base de tudo, testável sem UI.
2. **Caso de uso e API** (`MoverCandidatura`, schema, router). Depende do passo 1.
3. **Contrato e cliente** (regenerar tipos, `moverCandidatura` com `posicao`). Depende do passo 2.
4. **Spike do dnd-kit**: confirmar teclado no cartão com botão interno e toque com rolagem. Reduz o risco antes da UI final.
5. **`movimento.ts` e hook com atualização otimista**. Lógica pura primeiro.
6. **Componentes** (`ColunaKanban`, `CartaoCandidatura`, página) e remoção de `select` e "Detalhes".
7. **CSS responsivo e visual** (colunas fixas, rolagem, overlay, estados).
8. **E2E, acessibilidade e Postman.**

### Dependências Técnicas

- Instalar três pacotes novos do npm (lockfile atualizado).
- Python 3.12 para regenerar o schema, como no CI.

## Monitoramento e Observabilidade

- Backend: log `INFO` por movimento com `candidatura_id`, status de origem e destino e posição (sem dados pessoais). Log `WARNING` quando a posição é limitada ao fim da coluna.
- Frontend: erros de mutação passam pelo `registrar-erro.ts` existente, além do toast.
- Sem métricas novas; o projeto não tem pipeline de métricas.

## Considerações Técnicas

### Decisões Principais

- **`@dnd-kit` em vez de HTML5 nativo.** Dá teclado, toque, anúncios para leitor de tela e rolagem automática. O HTML5 nativo não funciona bem em celular e exigiria acessibilidade própria. Alternativa rejeitada: `react-beautiful-dnd` (descontinuada) e `@hello-pangea/dnd` (mais simples, mas o suporte a toque e a customização são menores).
- **Posição inteira por coluna, com renumeração.** Colunas têm poucas dezenas de cartões, então reescrever as posições da coluna de destino em uma transação é simples e correto. Alternativas rejeitadas: posição fracionária e lista ligada, que complicam sem ganho real nessa escala.
- **Regra de ordenação no domínio e persistência na porta.** O repositório só grava a ordem recebida. Isso segue Hexagonal e evita regra de negócio em SQL.
- **Um endpoint, não dois.** Mover e reordenar são o mesmo ato (destino = status + posição).
- **Atualização otimista com restauração.** O arrasto só parece fluido se o cartão não pular de volta enquanto a API responde.
- **Layout.** Largura fixa de coluna (272 px no desktop; `min(85vw, 320px)` no celular) com `scroll-snap-x`. Altura da área do board calculada com `100dvh` menos o topo, para funcionar com a barra do navegador móvel.

### Riscos Conhecidos

- **Botão dentro de elemento arrastável.** O ativador por teclado pode não ignorar o foco no título. Mitigação: spike no passo 4; plano B é usar uma alça de arraste no cartão.
- **Toque e rolagem.** Delay de 200 ms pode ser curto ou longo demais. Mitigação: teste em Safari iOS e Chrome Android; valor é constante em um só lugar.
- **Dois movimentos rápidos.** A resposta da primeira chamada pode chegar depois da segunda. Mitigação: `onMutate` cancela consultas pendentes e `onSettled` invalida; as mutações ficam em série por `mutationKey`.
- **Migração em banco existente.** Sem ferramenta de migração, a verificação por `PRAGMA` precisa ser idempotente. Coberta por teste.
- **Modal com dado desatualizado.** Hoje o modal recebe uma cópia da candidatura. Mitigação: guardar só o `id` e ler do cache.
- **Concorrência entre abas.** Duas abas podem reordenar a mesma coluna e a última vence. Aceito (usuário único por perfil).

### Conformidade com Padrões

Regras consultadas em `.windsurf/rules/` e `AGENTS.md`:

- `general-rules.md`: Clean Code, DRY, KISS/YAGNI, DDD, Hexagonal e TDD. Atendidos: regra no domínio, porta no repositório, funções puras testadas primeiro.
- `back-end-general-rules.md` e `code-design-standards.md`: camadas domínio, service layer, adapters e entrypoints; o caso de uso usa só portas. Sem desvios.
- `testing-rules.md`: testes unidade com fakes para portas e SQLite real nos testes de adapter.
- `AGENTS.md`: mudanças restritas ao pedido; reuso do `DetalheCandidaturaModal`, `Modal`, `useToast` e tokens existentes (pacote `frontend/src/shared/ui`).

Desvio: nova dependência de frontend (`@dnd-kit`), justificada acima. Sem outros desvios.

### Arquivos relevantes e dependentes

- `src/jobsync/candidatura/domain/candidatura.py`, `candidatura_repository.py`
- `src/jobsync/candidatura/adapters/candidatura_repository_impl.py`
- `src/jobsync/candidatura/service_layer/mover_candidatura/service.py`
- `src/jobsync/shared_kernel/adapters/persistence/_conexao_sqlite.py`
- `src/jobsync/entrypoints/api/schemas/candidatura.py`, `routers/candidatura_router.py`, `dependencies.py`
- `src/jobsync/entrypoints/streamlit_app.py` (usa `MoverCandidatura`; o parâmetro novo é opcional)
- `src/jobsync/tests/candidatura/*`, `src/jobsync/tests/entrypoints/api/test_routers.py`, `test_schemas.py`
- `frontend/src/features/candidaturas/*`, `frontend/src/api/*`, `frontend/src/shared/formatacao.ts`
- `frontend/e2e/fluxos.spec.ts`, `acessibilidade.spec.ts`, `apoio.ts`
- `job-sync.postman_collection.json`

## Questões em Aberto

1. A cor de cada coluna precisa de aprovação de design; o valor entra em `status.ts`.
2. Confirmar se o Streamlit deve mostrar a nova ordem. Hoje ele só usa `MoverCandidatura`, sem posição, então o movimento dele coloca o cartão no topo.

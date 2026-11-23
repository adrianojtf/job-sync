# Especificação Técnica — JOB-0041

## Resumo Executivo

Duas mudanças ligadas:

1. **Competências estruturadas.** O rascunho adaptado ganha `competencias` (categorias com tags), no mesmo padrão que `experiencias` já usa (estruturado ou seção de texto, nunca os dois). O texto "Rótulo: a, b" da IA é convertido em categorias por uma função de domínio. Na saída para o PDF, as categorias voltam a texto, e o gerador de PDF passa a destacar qualquer rótulo antes do primeiro ":" em vez de depender do catálogo fixo.
2. **Currículo adaptado persistido.** Novo contexto `curriculo_adaptado` (domínio, porta, repositório Postgres, casos de uso) guarda o conteúdo estruturado em JSONB. O PDF não é guardado: é regenerado a cada salvar. A edição posterior reusa a tela de revisão. O reuso como base entra como nova fonte em `AdaptarCurriculoRequest`.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Novos (backend):

- `curriculo_adaptado/domain/curriculo_adaptado.py`: agregado `CurriculoAdaptado`.
- `curriculo_adaptado/domain/curriculo_adaptado_repository.py`: porta.
- `curriculo_adaptado/adapters/curriculo_adaptado_repository_impl.py` e `_fake.py`: Postgres e fake de teste.
- `curriculo_adaptado/service_layer/`: `salvar_curriculo_adaptado`, `atualizar_curriculo_adaptado`, `buscar_curriculo_adaptado`, `listar_curriculos_adaptados`, cada um com `service.py`, `dtos.py` e `validator.py`, no padrão de `curriculo_salvo`.
- `curriculo/domain/competencias.py`: `CategoriaCompetencia` e funções `de_texto` e `para_texto`.
- Migração `0004_curriculo_adaptado.sql`.
- Router `curriculo_adaptado_router.py` e schemas.

Modificados (backend):

- `curriculo/domain/rascunho_curriculo_adaptado.py`: campo `competencias`, regra de exclusão mútua com a seção `TECNOLOGIAS`, conversão em `para_curriculo`.
- `curriculo/service_layer/adaptar_curriculo_para_vaga/service.py`: converte a seção `TECNOLOGIAS` da IA em `competencias`.
- `curriculo/adapters/gerador_pdf_client.py`: destaque do rótulo genérico (ver Decisões).
- `candidatura/service_layer/confirmar_candidatura_ajustada/*`: aceita `curriculo_adaptado_id` opcional e vincula.
- `curriculo_salvo/domain/curriculo_salvo_repository.py` e impls: novo método para atualizar o PDF.
- `entrypoints/api/schemas/curriculo.py` e `routers/curriculo_router.py`: `competencias` no rascunho; fonte `curriculo_adaptado_id` em `AdaptarCurriculoRequest`.
- Injeção de dependências dos serviços novos.

Novos (frontend, `frontend/src`):

- `shared/formulario-curriculo/EditorCompetencias.tsx` (+ css e teste): categorias e tags.
- `features/curriculos-adaptados/` (página de edição e `use-curriculos-adaptados.ts`).

Modificados (frontend):

- `features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx` e `formulario-revisao.ts`: bloco de competências no lugar do textarea de tecnologias; modo edição (salvar em vez de gerar).
- `features/ajustar-vaga/AjustarVagaPage.tsx`: usa o salvar currículo adaptado ao confirmar; ação "Editar currículo" em `CurriculoGerado`.
- `features/ajustar-vaga/fonte-curriculo.ts`: fonte `adaptado:<id>`.
- `features/curriculos/CurriculosPage.tsx` e `features/candidaturas/DetalheCandidaturaModal.tsx`: ponto de reabertura (a confirmar).
- `api/tipos` e cliente da API.

Fluxo: adaptar -> rascunho (competências estruturadas) -> revisar -> `POST /curriculos-adaptados` (salva e devolve PDF) -> confirmar candidatura (vincula) -> editar depois com `PUT` (regenera PDF e atualiza o PDF da candidatura).

## Design de Implementação

### Interfaces Principais

```python
class CurriculoAdaptadoRepository(ABC):
    def salvar(self, curriculo: CurriculoAdaptado) -> CurriculoAdaptado: ...
    def buscar(self, curriculo_id: str, perfil_identificador: str) -> CurriculoAdaptado | None: ...
    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoAdaptado, ...]: ...
    def vincular_curriculo_salvo(
        self, curriculo_id: str, perfil_identificador: str, curriculo_salvo_id: str
    ) -> None: ...
```

```python
@dataclass(frozen=True)
class CategoriaCompetencia:
    nome: str
    tags: tuple[str, ...]
    @classmethod
    def revisada(cls, nome: str, tags: Iterable[str]) -> "CategoriaCompetencia | None": ...
```

`revisada` aplica trim, descarta tag vazia e duplicada (sem diferenciar caixa) e devolve `None` para categoria sem nome ou sem tags, como `ExperienciaAdaptada.revisada`.

`de_texto(conteudo)` lê linhas "Rótulo: a, b" (aceitando marcadores `-•*`). Linha sem rótulo vai para a categoria "Tecnologias". `para_texto` gera "Rótulo: a, b", uma categoria por linha.

### Modelos de Dados

`CurriculoAdaptado`: `id`, `perfil_identificador`, `nome_referencia`, `cargo_alvo`, `empresa_alvo`, `idioma_alvo`, `descricao_vaga`, `analise_vaga`, `rascunho` (`RascunhoCurriculoAdaptado`), `curriculo_salvo_id | None`, `criado_em`, `atualizado_em`. Método `com_rascunho_revisado(rascunho, agora)` devolve nova instância (imutável, Tell Don't Ask).

Tabela:

```sql
CREATE TABLE curriculo_adaptado (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    nome_referencia TEXT NOT NULL,
    cargo_alvo TEXT NOT NULL,
    empresa_alvo TEXT NOT NULL,
    idioma_alvo TEXT NOT NULL,
    descricao_vaga TEXT NOT NULL,
    analise_vaga_json JSONB NOT NULL DEFAULT '{}',
    conteudo_json JSONB NOT NULL,
    curriculo_salvo_id TEXT,
    criado_em TIMESTAMPTZ NOT NULL,
    atualizado_em TIMESTAMPTZ NOT NULL
);
CREATE INDEX ix_curriculo_adaptado_perfil ON curriculo_adaptado (perfil_identificador, atualizado_em DESC);
```

`curriculo_salvo_id` sem chave estrangeira, seguindo a decisão da migração 0002 (remover um currículo salvo é permitido e a tela lida com ausência). A busca de PDF a atualizar trata o currículo ausente.

### Endpoints de API

Todos sob `exigir_perfil_da_requisicao`, filtrando por perfil.

- `POST /curriculos-adaptados`: salva o rascunho revisado com os dados da vaga; devolve `id` e o PDF (mesmo formato de `CurriculoRevisadoResponse`). Substitui `POST /curriculos-revisados` na tela de ajuste; o endpoint antigo permanece.
- `GET /curriculos-adaptados`: lista resumida (id, nome, cargo, empresa, atualizado em).
- `GET /curriculos-adaptados/{id}`: conteúdo completo e contexto da vaga.
- `PUT /curriculos-adaptados/{id}`: substitui o rascunho, regenera o PDF, atualiza `curriculo_salvo` vinculado; devolve o PDF.
- `POST /curriculos/{id}/rascunhos-adaptados` com `curriculo_adaptado_id` como nova fonte (alternativa a `perfil_identificador` e `pdf_base64`).
- `POST /candidaturas-ajustadas` (rota existente em `candidatura_router.py`): campo opcional `curriculo_adaptado_id`.

Erros: 404 se o id não pertence ao perfil; 422 para conteúdo inválido.

## Pontos de Integração

- `curriculo_adaptado` consome `curriculo` pela API pública do pacote (`RascunhoCurriculoAdaptado`, `GeradorPdfPort`), como `vaga` consome seus vizinhos.
- Gravações em repositórios diferentes não são transacionais (padrão já documentado em `ConfirmarCandidaturaAjustada`). Na atualização, a ordem é: gerar PDF, atualizar `curriculo_adaptado`, atualizar `curriculo_salvo`. Falha no último passo é registrada em log e a resposta devolve o PDF novo; o próximo salvar corrige. Esta política é uma proposta.

## Abordagem de Testes

### Testes Unidade

Pytest, TDD, regras de `testing-rules.md`, repositório fake:

- `CategoriaCompetencia.revisada`: trim, duplicadas, vazia.
- `de_texto`/`para_texto`: ida e volta, marcadores, linha sem rótulo, rótulo com ":" no meio.
- `RascunhoCurriculoAdaptado`: exclusão mútua competências/seção; `para_curriculo` gera a seção na ordem certa.
- `AdaptarCurriculoParaVaga`: seção `TECNOLOGIAS` da IA vira `competencias`.
- Serviços novos: salvar, atualizar (isolamento por perfil, 404, atualiza PDF vinculado), listar, vincular na confirmação.
- Gerador de PDF: rótulo customizado em negrito, uma categoria por linha, rótulo do catálogo ainda traduzido.
- Adaptação a partir de `curriculo_adaptado_id`: monta o currículo base sem alterar o original.
- Teste de repositório Postgres seguindo `test_*_repository_impl.py` existentes.

Frontend (Vitest e Testing Library): `EditorCompetencias` (remover, criar com Enter e vírgula, duplicada, renomear/criar/excluir categoria, rótulos acessíveis); `formulario-revisao` (ida e volta rascunho/formulário); fluxo de edição e fonte `adaptado`.

### Testes de Serviço

Playwright (`frontend/e2e`): gerar, remover uma tag, confirmar, "Editar currículo", recarregar e reabrir, usar como base de outra vaga.

## Sequenciamento de Desenvolvimento

1. `Competencias` e rascunho (domínio puro, sem I/O).
2. Gerador de PDF com rótulo genérico.
3. Migração, `curriculo_adaptado` (domínio, repositório, casos de uso) e endpoints.
4. Vínculo com `ConfirmarCandidaturaAjustada` e atualização do `curriculo_salvo`.
5. `EditorCompetencias` e revisão.
6. Salvar/editar na tela de ajuste e ponto de reabertura.
7. Fonte `adaptado` na adaptação.
8. E2E.

Cada etapa entrega algo testável sozinha. As etapas 1 e 5 já entregam o ponto 2 do pedido original (tags) sem a persistência.

## Monitoramento e Observabilidade

Logs `info` ao salvar e atualizar (ids, contagem de categorias e experiências, tamanho do PDF), sem conteúdo do currículo. `warning` quando a atualização do `curriculo_salvo` falha.

## Considerações Técnicas

### Decisões Principais

- **Estruturado em `competencias`, não texto com parser na tela.** Evita ambiguidade ao editar e segue o padrão de `experiencias`. Alternativa rejeitada: manter texto e quebrar no navegador, que duplica o parser em dois lugares.
- **Rótulo genérico no PDF.** `_negritar_categorias_tecnologia` e `_quebrar_categorias` só reconhecem rótulos do catálogo (`categorias_tecnologia`). Com nomes livres, a categoria nova não sairia em negrito. Como `competencias` já chega com uma categoria por linha, o gerador passa a destacar o texto antes do primeiro ":" e a tradução do catálogo continua para rótulos conhecidos.
- **PDF não guardado no objeto.** Escolha do usuário: evita PDF defasado do conteúdo. Custo: regenerar ao salvar.
- **Contexto próprio `curriculo_adaptado`**, distinto de `curriculo_salvo` (PDF bruto) e de `curriculo` (domínio de geração).
- **Guarda `descricao_vaga` e `analise_vaga`** para as Sugestões de IA da edição posterior sem nova análise.

### Riscos Conhecidos

- Rascunhos e PDFs antigos não têm objeto salvo: só currículos criados depois da entrega são editáveis. Sem migração de dados.
- Sem transação entre repositórios: possível PDF da candidatura defasado se o último passo falhar (mitigado por log e novo salvar).
- Base com tecnologia trocada: efeito composto da JOB-0037 (Questões em Aberto do PRD).
- Layout do PDF de referência (coluna de rótulos) pode exigir mudança maior em `estilo_curriculo_pdf.py`. Depende da decisão do PRD.
- `conteudo_json` evolui com o rascunho: incluir campo de versão do formato para leitura futura (proposta).

### Conformidade com Padrões

- `AGENTS.md`: DDD, portas e adaptadores, imutabilidade, TDD, DRY (reuso do padrão `revisada`).
- `.windsurf/rules/testing-rules.md`: testes.
- `code-design-standards.md`, `back-end-general-rules.md` e `general-rules.md`: a revisar no início das tasks (não lidos nesta fase).

### Arquivos relevantes e dependentes

- `src/jobsync/curriculo/domain/rascunho_curriculo_adaptado.py`, `curriculo.py`
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/service.py`
- `src/jobsync/curriculo/adapters/gerador_pdf_client.py`
- `src/jobsync/curriculo_salvo/` (modelo para o novo contexto)
- `src/jobsync/candidatura/service_layer/confirmar_candidatura_ajustada/`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`, `schemas/curriculo.py`
- `src/jobsync/shared_kernel/adapters/persistence/migracoes/`
- `frontend/src/features/ajustar-vaga/`, `features/curriculos/`, `features/candidaturas/`, `shared/formulario-curriculo/`

## Decisões tomadas na implementação

- **Fonte `curriculo_adaptado_id` em três endpoints.** O seletor de base é compartilhado, então o rascunho (`/curriculos/{id}/rascunhos-adaptados`), a análise ATS e a carta aceitam a nova fonte. O endpoint legado `/curriculos/{id}/adaptacoes` não muda. `perfil_identificador` segue obrigatório com a nova fonte (identifica o dono e passa pela checagem de sessão); o perfil estruturado não é consultado.
- **Base com troca de tecnologia (JOB-0037).** A nova adaptação trata o texto do currículo salvo como original, inclusive tecnologias que uma adaptação anterior trocou. Decisão do PRD (Questões em Aberto 4): aceitar e documentar.
- **Pontos de reabertura.** Os dois foram entregues: "Meus currículos" (painel "Currículos adaptados") e o detalhe da candidatura. O vínculo do detalhe vem do cruzamento de `curriculo_salvo_id` no frontend, sem mudança de backend.
- **`vincular_curriculo_salvo` recebe o perfil**, para nunca alterar o currículo de outro perfil.
- **Categorias vazias** (sem nome ou sem tags) são descartadas na tela e no servidor, para a edição reaberta mostrar o que foi salvo.
- **Não entregues:** layout de coluna de rótulos no PDF, limite de currículos adaptados por perfil e migração de currículos criados antes desta entrega (PRD, Questões em Aberto 1, 3 e sem migração de dados).

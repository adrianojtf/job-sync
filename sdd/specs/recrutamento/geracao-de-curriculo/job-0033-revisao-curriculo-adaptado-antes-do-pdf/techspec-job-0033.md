# Especificação Técnica — JOB-0033

PRD de referência: `prd-job-0033.md` (mesmo diretório).

## Resumo Executivo

A adaptação via IA (`AdaptarCurriculoParaVaga`) deixa de gerar PDF. Ela passa a devolver um agregado de domínio novo, `RascunhoCurriculoAdaptado`, com cabeçalho, seções de texto e experiências estruturadas (quando a fonte é o perfil). A geração do PDF vira um caso de uso próprio, `GerarPdfCurriculoRevisado`, que recebe o rascunho revisado e só depende da porta `GeradorPdfPort`. A adaptação perde a dependência de `GeradorPdfPort`.

O rascunho não é persistido. A API devolve o rascunho, o frontend o mantém em memória durante a revisão e envia o rascunho completo na confirmação. O fluxo legado (`POST /curriculos/{id}/adaptacoes`, `?download=true` e Streamlit) mantém o contrato: o entrypoint compõe os dois casos de uso em sequência, sem revisão. No frontend, os blocos do formulário de "Meu perfil" são extraídos para `shared/formulario-curriculo` e reaproveitados pela nova tela de revisão.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Backend (`src/jobsync`):

| Componente | Tipo | Situação | Responsabilidade |
|---|---|---|---|
| `curriculo/domain/rascunho_curriculo_adaptado.py` → `RascunhoCurriculoAdaptado` | Agregado | **Novo** | Estado completo do currículo em revisão; converte para `Curriculo` |
| `curriculo/service_layer/adaptar_curriculo_para_vaga/service.py` → `AdaptarCurriculoParaVaga` | Caso de uso | **Modificado** | Produz o rascunho; não gera mais PDF |
| `curriculo/service_layer/adaptar_curriculo_para_vaga/dtos.py` | DTOs | **Modificado** | Output troca `pdf_bytes`/`nome_arquivo` por `rascunho` |
| `curriculo/service_layer/gerar_pdf_curriculo_revisado/` → `GerarPdfCurriculoRevisado` | Caso de uso | **Novo** | Confirmação: rascunho → `Curriculo` → PDF + nome do arquivo |
| `entrypoints/api/schemas/curriculo.py` | Schemas | **Modificado** | Schemas do rascunho e da confirmação |
| `entrypoints/api/routers/curriculo_router.py` | Router | **Modificado** | 2 endpoints novos; `/adaptacoes` compõe os dois casos de uso |
| `entrypoints/api/dependencies.py` | DI | **Modificado** | Remove `gerador_pdf` da adaptação; registra o novo caso de uso |
| `entrypoints/streamlit_app.py` | UI legada | **Modificado** | Compõe adaptação + geração de PDF (comportamento inalterado) |

Frontend (`frontend/src`):

| Componente | Situação | Responsabilidade |
|---|---|---|
| `shared/formulario-curriculo/ListaItensCurriculo.tsx` | **Novo (extraído)** | Lista editável genérica; substitui `features/perfil/ListaItensPerfil.tsx` |
| `shared/formulario-curriculo/PainelDadosPessoais.tsx` | **Novo (extraído)** | Nome, e-mail, LinkedIn e resumo profissional |
| `shared/formulario-curriculo/campos-curriculo.ts` | **Novo (extraído)** | `CAMPOS_EXPERIENCIA`, `EXPERIENCIA_VAZIA`, `ExperienciaFormulario` |
| `shared/formulario-curriculo/FormularioCurriculo.module.css` | **Novo (extraído)** | Estilos de grade, item, legenda e rodapé hoje em `PerfilPage.module.css` |
| `features/perfil/PerfilPage.tsx` | **Modificado** | Passa a compor os blocos compartilhados (sem mudança de comportamento) |
| `features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx` | **Novo** | Tela de revisão e confirmação |
| `features/ajustar-vaga/formulario-revisao.ts` | **Novo** | Mapeia rascunho ↔ formulário |
| `features/ajustar-vaga/AjustarVagaPage.tsx` | **Modificado** | Máquina de etapas: `vaga` → `revisao` → `vaga` com PDF pronto |
| `features/ajustar-vaga/use-ajustar-vaga.ts` | **Modificado** | Mutations `gerarRascunho` e `gerarPdf` no lugar de `adaptar` |
| `api/api-client.ts`, `api/http-api-client.ts`, `api/tipos.ts`, `api/schema.d.ts` | **Modificado** | Novos métodos e tipos (schema regenerado por `npm run gerar-tipos`) |

Fluxo de dados (React):

```
AjustarVagaPage ──POST /curriculos/{id}/rascunhos-adaptados──▶ AdaptarCurriculoParaVaga
      │                                                     (IA, sem PDF) ──▶ RascunhoCurriculoAdaptado
      ▼ (rascunho em memória, react-hook-form)
RevisaoCurriculoAdaptado ──POST /curriculos-revisados──▶ GerarPdfCurriculoRevisado ──▶ GeradorPdfPort
      ▼
CurriculoGerado (Baixar PDF)
```

## Design de Implementação

### Interfaces Principais

Agregado de domínio (`curriculo/domain/rascunho_curriculo_adaptado.py`):

```python
@dataclass(frozen=True)
class RascunhoCurriculoAdaptado:
    """Currículo adaptado em revisão. Seções são partes do mesmo agregado."""
    nome_completo: str
    email: str
    linkedin: str
    secoes: tuple[SecaoCurriculo, ...]
    experiencias: tuple[ExperienciaParaAvaliacao, ...] | None = None

    @classmethod
    def revisado(cls, nome_completo: str, email: str, linkedin: str,
                 secoes: Iterable[tuple[TipoSecao, str, str]],
                 experiencias: Iterable[ExperienciaParaAvaliacao] | None) -> "RascunhoCurriculoAdaptado":
        """Monta a partir da edição do usuário: descarta seções e experiências em branco."""

    def para_curriculo(self) -> Curriculo:
        """Converte para o Curriculo consumido por GeradorPdfPort."""
```

Invariantes (`__post_init__`, `ValueError`):

- `nome_completo` obrigatório.
- Pelo menos uma seção com conteúdo ou uma experiência.
- Se `experiencias` não for `None`, `secoes` não pode conter `TipoSecao.EXPERIENCIAS` (fonte única).
- Cada experiência estruturada exige `cargo` e `empresa` (mesma regra do cadastro).

`para_curriculo()` absorve a lógica hoje em `AdaptarCurriculoParaVaga._montar_secao_experiencias` (formato `Cargo — Empresa (Período)\nDescrição`). O método estático é removido do caso de uso (DRY). O formato precisa continuar idêntico, porque `GeradorPdfClient._formatar_conteudo_experiencias` separa blocos por linha em branco e põe em negrito a primeira linha de cada bloco.

Caso de uso de confirmação (`curriculo/service_layer/gerar_pdf_curriculo_revisado/`):

```python
@dataclass(frozen=True)
class GerarPdfCurriculoRevisadoInputDto:
    rascunho: RascunhoCurriculoAdaptado
    idioma_alvo: str
    cargo_alvo: str
    empresa_alvo: str
    data_referencia: date | None = None

@dataclass(frozen=True)
class GerarPdfCurriculoRevisadoOutputDto:
    pdf_bytes: bytes
    nome_arquivo: NomeArquivo

class GerarPdfCurriculoRevisado:
    def __init__(self, gerador_pdf: GeradorPdfPort) -> None: ...
    def executar(self, input_dto: GerarPdfCurriculoRevisadoInputDto) -> GerarPdfCurriculoRevisadoOutputDto: ...
```

O `GerarPdfCurriculoRevisadoInputValidator` reaproveita `IDIOMAS_SUPORTADOS` e as regras de cargo/empresa de `adaptar_curriculo_para_vaga/validator.py`. Para evitar duplicação, essas regras sobem para um módulo comum em `curriculo/service_layer/validacoes_vaga_alvo.py`, usado pelos dois validators. O `NomeArquivo` usa `rascunho.nome_completo` (nome revisado).

Caso de uso de adaptação (mudanças):

- Construtor: remove `gerador_pdf`.
- `executar`: após `_ajustar_todas_as_secoes`, monta `RascunhoCurriculoAdaptado(nome, email, linkedin, secoes_sem_experiencias_quando_estruturadas, experiencias_adaptadas or None)`.
- Output: `rascunho`, `curriculo_adaptado` (= `rascunho.para_curriculo()`, mantido para a carta), `analise_vaga`, avaliações. Saem `pdf_bytes` e `nome_arquivo`.

### Modelos de Dados

Sem banco de dados. Contrato JSON do rascunho (`RascunhoCurriculoAdaptadoSchema`, usado na resposta e na requisição de confirmação):

```json
{
  "nome_completo": "Ana Souza",
  "email": "ana@ex.com",
  "linkedin": "https://linkedin.com/in/ana",
  "secoes": [
    {"tipo": "PERFIL", "titulo": "Perfil", "conteudo": "..."},
    {"tipo": "TECNOLOGIAS", "titulo": "Tecnologias", "conteudo": "Linguagens: Java, Python"}
  ],
  "experiencias": [
    {"cargo": "Dev Backend", "empresa": "TechCorp", "periodo": "2022 - Atual", "descricao": "..."}
  ]
}
```

- `tipo`: `Literal` com os nomes de `TipoSecao`.
- `experiencias`: `null` quando a fonte é PDF; nesse caso a seção `EXPERIENCIAS` vem em `secoes`.
- `titulo` vem da IA e não é editável na UI; o PDF continua traduzindo títulos via `CatalogoLocalizacao`.
- `to_domain()` chama `RascunhoCurriculoAdaptado.revisado(...)`; `from_domain()` faz o inverso.

Formulário de revisão (`formulario-revisao.ts`):

```ts
interface FormularioRevisao {
  nome_completo: string; email: string; linkedin: string;
  resumo_profissional: string;          // ⇄ seção PERFIL
  experiencias: ExperienciaFormulario[] | null;
  experiencias_texto: string;           // ⇄ seção EXPERIENCIAS (fonte PDF)
  secoes: { tipo: TipoSecaoTexto; titulo: string; conteudo: string }[]; // TECNOLOGIAS, FORMACAO, CERTIFICACOES, IDIOMAS
}
rascunhoParaFormulario(r: RascunhoCurriculoAdaptado): FormularioRevisao
formularioParaRascunho(f: FormularioRevisao): RascunhoCurriculoAdaptado
```

### Endpoints de API

| Método e caminho | Situação | Descrição |
|---|---|---|
| `POST /curriculos/{id}/rascunhos-adaptados` | **Novo** | Body = `AdaptarCurriculoRequest` (sem mudança). Executa a IA e devolve `RascunhoAdaptadoResponse` (`rascunho`, `avaliacao_vaga`, `status_avaliacao_vaga`, `avaliacoes_experiencias`). **200**, pois nada é persistido. 422 para entrada inválida. |
| `POST /curriculos-revisados` | **Novo** | Body = `GerarPdfCurriculoRevisadoRequest` (`rascunho`, `idioma_alvo`, `cargo_alvo`, `empresa_alvo`, `data_referencia?`). Devolve `{nome_arquivo, pdf_base64}` (**200**); `?download=true` devolve `application/pdf`, como `/adaptacoes`. 422 quando o rascunho viola invariantes. |
| `POST /curriculos/{id}/adaptacoes` | **Contrato inalterado** | Router compõe `AdaptarCurriculoParaVaga` + `GerarPdfCurriculoRevisado` sobre o rascunho não revisado. |
| `POST /cartas-apresentacao` | **Contrato inalterado** | Continua usando `output.curriculo_adaptado`; deixa de gerar um PDF descartado (ganho de performance). |

Atualizar `job-sync.postman_collection.json` com os dois endpoints novos.

## Pontos de Integração

Nenhuma integração externa nova. A IA (OpenAI/Jev) continua chamada só na adaptação. A confirmação usa apenas ReportLab (`GeradorPdfClient`), sem rede. Erros de validação do domínio (`ValueError`) viram 422 pelo padrão atual dos routers (`try/except ValueError` → `HTTPException(422)`).

## Abordagem de Testes

TDD (Red-Green-Refactor), seguindo `.windsurf/rules/testing-rules.md`: classes `Test<ClasseSobTeste>`, blocos AAA separados, mocks apenas com `unittest.mock` e só para portas externas.

### Testes Unidade

Backend:

- `tests/curriculo/test_rascunho_curriculo_adaptado.py` (`TestRascunhoCurriculoAdaptado`):
  - `para_curriculo` gera a seção `EXPERIENCIAS` no formato atual a partir das experiências estruturadas.
  - `revisado` descarta seções e experiências em branco.
  - Invariantes: nome vazio, rascunho vazio, `EXPERIENCIAS` duplicada, experiência sem cargo/empresa.
- `tests/curriculo/test_gerar_pdf_curriculo_revisado_service.py`:
  - Envia ao `GeradorPdfPort` (mock) o `Curriculo` com o conteúdo **editado** (critério "PDF reflete o revisado").
  - Nome do arquivo usa o nome revisado; validações de idioma, cargo e empresa.
- `tests/curriculo/test_adaptar_curriculo_para_vaga_service.py` (ajuste):
  - Remover `gerador_pdf` dos construtores; afirmar o `rascunho` no output.
  - Garantir que nenhum PDF é gerado na adaptação (a porta deixa de ser dependência).
- `tests/entrypoints/api/test_routers.py` e `test_schemas.py`:
  - Novos endpoints: sucesso, 422, `?download=true`.
  - `/adaptacoes` e `/cartas-apresentacao` com contrato idêntico ao atual (regressão).

Frontend (Vitest + Testing Library):

- `formulario-revisao.test.ts`: ida e volta rascunho ↔ formulário, com e sem experiências estruturadas.
- `RevisaoCurriculoAdaptado.test.tsx`: todas as seções visíveis e editáveis ao mesmo tempo; confirmação envia o estado editado; erro de validação bloqueia o envio; falha da API preserva as edições; "Voltar para a vaga" com alterações abre `ConfirmacaoModal`.
- `AjustarVagaPage.test.tsx` (ajuste): "Gerar currículo adaptado" abre a revisão e não mostra "Baixar PDF"; após confirmar, "Baixar PDF" aparece.
- `PerfilPage.test.tsx`: deve passar **sem alteração** (prova de que a extração dos componentes não mudou o cadastro).

### Testes de Serviço

- `frontend/e2e/fluxos.spec.ts`: ajustar o fluxo "Gerar currículo adaptado" para passar pela revisão, editar um campo e confirmar.
- `frontend/e2e/acessibilidade.spec.ts`: incluir a etapa de revisão.
- Teste de contrato no CI: regenerar `schema.d.ts` (`npm run gerar-tipos`) e versionar.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. **Agregado `RascunhoCurriculoAdaptado`** e testes. Base de todo o resto; sem dependências.
2. **`GerarPdfCurriculoRevisado`** e validação comum. Depende do item 1.
3. **Refatorar `AdaptarCurriculoParaVaga`** para devolver o rascunho; remover `gerador_pdf`; ajustar DI, Streamlit e `/adaptacoes`/`/cartas-apresentacao` para manter o comportamento legado.
4. **Schemas e endpoints novos** (`/rascunhos-adaptados`, `/curriculos-revisados`) e Postman.
5. **Extração dos componentes de "Meu perfil"** para `shared/formulario-curriculo`, com `PerfilPage.test.tsx` verde e intocado (refatoração pura).
6. **Cliente de API e tipos** (regenerar `schema.d.ts`).
7. **Tela `RevisaoCurriculoAdaptado`** e integração em `AjustarVagaPage`.
8. **E2E e acessibilidade.**

### Dependências Técnicas

Nenhuma infraestrutura nova. Nenhuma biblioteca nova (reuso de `react-hook-form`, `@tanstack/react-query`, FastAPI, Pydantic, ReportLab).

## Monitoramento e Observabilidade

Usar o `logging` já configurado nos casos de uso:

- `INFO` em `GerarPdfCurriculoRevisado`: "PDF gerado a partir de rascunho revisado" com contagens (`secoes`, `experiencias`) e idioma. **Sem** nome, e-mail ou conteúdo.
- `INFO` em `AdaptarCurriculoParaVaga`: "Rascunho adaptado gerado" com as mesmas contagens.
- `WARNING` já existentes para indisponibilidade do Jev permanecem.
- Erros 422 seguem o padrão atual dos routers (`ValueError` → `HTTPException(422)`); erros de schema seguem o handler de `entrypoints/api/exceptions.py`.

## Considerações Técnicas

### Decisões Principais

1. **Rascunho no frontend, não no servidor.** O caso de uso de confirmação é sem estado: recebe o rascunho completo. Justificativa: KISS/YAGNI, sem TTL, sem limpeza e sem condição de corrida entre abas. Trade-off: recarregar a página perde o rascunho (aceito no PRD).
2. **Modelo híbrido.** Dados pessoais e experiências estruturadas usam os campos do cadastro. As demais seções ficam como texto, porque é o que a IA já devolve (`AjustadorTextoPort.ajustar_secao`). Rejeitado: estruturar todas as seções, porque exigiria mudar prompts e parsers da IA (escopo maior, risco de regressão na tradução).
3. **Composição de blocos, não componente único com `modo`.** As duas telas compartilham `PainelDadosPessoais`, `ListaItensCurriculo` e `CAMPOS_EXPERIENCIA`, mas diferem nas outras seções. Um componente único com `modo="cadastro" | "revisao"` encheria o código de condicionais. A composição atende o DRY pedido na nota de design sem esse custo.
4. **Novos recursos em vez de mudar `/adaptacoes`.** Atende a regra "só altere contrato quando solicitado" e a decisão de manter o Streamlit e o `?download=true`.
5. **Adaptação sem `GeradorPdfPort`.** Concretiza o desacoplamento da nota de design. O efeito colateral positivo é que `/cartas-apresentacao` deixa de gerar um PDF inútil.
6. **Etapa na mesma rota (`/ajustar-vaga`).** A revisão substitui o conteúdo da página. Isso preserva os resultados de "Analisar vaga", ATS e carta, sem passar o rascunho por `location.state`.

### Riscos Conhecidos

- **Formato da seção de experiências:** o PDF põe em negrito a primeira linha de cada bloco (`Cargo — Empresa (Período)`). Mitigação: o teste do agregado fixa o formato; o teste existente de `GeradorPdfClient` cobre a renderização.
- **Edição de texto pela fonte PDF:** o usuário pode quebrar padrões que o PDF reconhece (ex.: categorias de tecnologias "Rótulo: itens"). Mitigação: texto de ajuda nos campos de texto; risco baixo, porque o PDF cai no parágrafo simples.
- **Regressão em "Meu perfil" na extração:** mitigação pelo teste de página inalterado (item 5 da ordem).
- **Tamanho do payload:** o rascunho tem poucos KB; sem risco relevante.

### Conformidade com Padrões

- `code-design-standards.md`: agregado em `curriculo/domain` sem infraestrutura; casos de uso em pacotes por funcionalidade (`service.py`, `dtos.py`, `validator.py`, `__init__.py`); método `executar`; injeção via construtor; nenhum service usa outro service (a composição legada fica no entrypoint, como já ocorre em `/cartas-apresentacao`); entrypoints convertem para DTO/schema.
- `back-end-general-rules.md`: recursos com substantivos no plural (`rascunhos-adaptados`, `curriculos-revisados`); POST para ação não-CRUD; 200 sem persistência (não 201); 422 para regra de domínio; contrato existente preservado.
- `testing-rules.md`: `Test<Classe>`, AAA, sem comentários, `unittest.mock` só para portas externas, sem alterar produção para testar.
- `AGENTS.md`: DRY, Tell Don't Ask (`rascunho.para_curriculo()`), hexagonal, TDD.

**Desvio documentado:** a nota de design da issue sugeria um caso de uso que "mantém o estado em memória/sessão" no backend. Pela decisão 1, o estado fica na sessão da tela, e o caso de uso de revisão vira o caso de uso de confirmação (`GerarPdfCurriculoRevisado`). O desacoplamento entre IA e PDF é mantido.

### Arquivos relevantes e dependentes

- `src/jobsync/curriculo/domain/curriculo.py`, `avaliacao_experiencia.py`, `gerador_pdf_port.py`
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/{service,dtos,validator}.py`
- `src/jobsync/curriculo/adapters/gerador_pdf_client.py` (sem mudança; dependente do formato)
- `src/jobsync/entrypoints/api/{dependencies.py,routers/curriculo_router.py,schemas/curriculo.py}`
- `src/jobsync/entrypoints/streamlit_app.py`
- `src/jobsync/vaga_externa/service_layer/candidatar_na_vaga_externa/service.py` (fora de escopo; não usa o caso de uso alterado)
- `src/jobsync/tests/curriculo/test_adaptar_curriculo_para_vaga_service.py`, `tests/entrypoints/api/test_routers.py`, `test_schemas.py`
- `frontend/src/features/perfil/{PerfilPage.tsx,ListaItensPerfil.tsx,formulario-perfil.ts,PerfilPage.module.css}`
- `frontend/src/features/ajustar-vaga/{AjustarVagaPage.tsx,use-ajustar-vaga.ts}`
- `frontend/src/api/{api-client.ts,http-api-client.ts,tipos.ts,schema.d.ts}`
- `frontend/e2e/{fluxos.spec.ts,acessibilidade.spec.ts}`
- `job-sync.postman_collection.json`

## Questões em Aberto

1. Guardar o rascunho em `sessionStorage` para sobreviver a um recarregamento? (fora do escopo atual; baixo custo se for pedido)
2. Mostrar as avaliações Jev das experiências na tela de revisão ou só na visão de resultados? Proposta: na revisão, ao lado de cada experiência, com o rótulo "avaliação do texto sugerido pela IA".
3. Renomear o botão "Gerar currículo adaptado" para "Adaptar currículo", já que ele não gera mais o PDF? Exige ajuste no E2E.

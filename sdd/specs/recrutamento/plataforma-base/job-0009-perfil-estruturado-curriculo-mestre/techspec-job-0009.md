# Especificação Técnica

## Resumo Executivo

Esta Tech Spec descreve a implementação do Perfil Estruturado (`prd-job-0009.md`): um novo agregado de domínio (`PerfilEstruturado`, com sub-entidades `ExperienciaProfissional`, `FormacaoAcademica`, `Certificacao`, `Idioma`) persistido por perfil de login, mais um Domain Service que o converte para o `Curriculo` já existente (`MontarCurriculoDoPerfilEstruturado`), permitindo que `AdaptarCurriculoParaVaga`, `AnalisarAtsVaga` e `CandidatarNaVagaExterna` recebam um `Curriculo` pronto em vez de extraí-lo de um PDF a cada chamada. Um novo use case (`ImportarPerfilDePdf`) reaproveita a extração de texto já existente (`ExtratorTextoPdfPlumber`) com um novo prompt de IA que produz diretamente os campos estruturados, usado para pré-preencher o formulário de perfil a partir de um PDF (biblioteca existente ou export do LinkedIn) — sempre revisável antes de salvar, nunca persistido automaticamente.

A mudança central nos três use cases existentes é mínima por design: cada um ganha um campo opcional `curriculo_pre_montado: Curriculo | None` no InputDto; quando presente, o use case pula a chamada a `ExtratorCurriculoPort` inteiramente. Isso preserva 100% da lógica de adaptação/análise/candidatura já implementada e testada nas Fases 0-3, sem duplicar nada — só muda de onde o `Curriculo` inicial vem.

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `PerfilEstruturado` (novo, `src/domain/perfil_estruturado/__init__.py`): agregado raiz — `perfil_identificador`, `nome_completo`, `email`, `linkedin`, `resumo_profissional`, `experiencias: tuple[ExperienciaProfissional, ...]`, `formacoes: tuple[FormacaoAcademica, ...]`, `certificacoes: tuple[Certificacao, ...]`, `idiomas: tuple[Idioma, ...]`, `tecnologias: tuple[str, ...]`.
- `ExperienciaProfissional`, `FormacaoAcademica`, `Certificacao`, `Idioma`, `NivelIdioma` (novos, mesmo módulo): value objects imutáveis. `periodo` é texto livre (ex: "Jan 2020 - Dez 2022", "2023 - Atual") em vez de datas estritas — decisão de simplicidade de UX (usuário raramente sabe o dia exato).
- `DadosPerfilExtraidos` (novo, mesmo módulo): mesma forma de `PerfilEstruturado` mas sem `perfil_identificador` — é o "rascunho" devolvido pela extração de PDF, antes de ser associado a um perfil de login e salvo.
- `PerfilEstruturadoRepository` (novo, `src/domain/perfil_estruturado/perfil_estruturado_repository.py`): porta — `salvar`, `buscar_por_perfil`.
- `ExtratorPerfilEstruturadoPort` (novo, `src/domain/perfil_estruturado/extrator_perfil_estruturado_port.py`): porta — `extrair(pdf_bytes) -> DadosPerfilExtraidos`.
- `MontarCurriculoDoPerfilEstruturado` (novo Domain Service, `src/domain/perfil_estruturado/montar_curriculo_do_perfil_estruturado_service.py`): transformação pura e determinística `PerfilEstruturado -> Curriculo | None` (retorna `None` se não houver conteúdo mínimo, ver "Decisões Principais").
- `PerfilEstruturadoRepositoryImpl` (novo, `src/infrastructure/persistence/perfil_estruturado_repository_impl.py`): uma linha por perfil (upsert), sub-listas serializadas como JSON — sem histórico/versionamento (decisão confirmada no PRD).
- `ExtratorPerfilEstruturadoGroq` (novo, `src/infrastructure/llm/extrator_perfil_estruturado_groq.py`): reaproveita `ExtratorTextoPdfPlumber` (já existente) + `ClienteGroq.solicitar_json` (já existente) com um novo prompt que pede a estrutura completa em JSON.
- `SalvarPerfilEstruturado`, `BuscarPerfilEstruturado`, `ImportarPerfilDePdf` (novos use cases, `src/application/use_cases/`): ver "Interfaces Principais".
- `AdaptarCurriculoParaVaga`, `AnalisarAtsVaga`, `CandidatarNaVagaExterna` (existentes, modificados): ganham `curriculo_pre_montado: Curriculo | None = None` no InputDto — quando presente, pulam `ExtratorCurriculoPort.extrair(...)`.

Fluxo de dados — salvar perfil (preenchimento manual ou edição):
1. UI monta os campos do formulário e chama `SalvarPerfilEstruturado.executar(input_dto)`.
2. Use case valida (nome/email obrigatórios) e chama `PerfilEstruturadoRepository.salvar(...)` (upsert).

Fluxo de dados — importar de PDF:
1. UI chama `ImportarPerfilDePdf.executar(ImportarPerfilDePdfInputDto(pdf_curriculo=...))`.
2. Use case chama `ExtratorPerfilEstruturadoPort.extrair(pdf_bytes)` → `DadosPerfilExtraidos`.
3. UI pré-preenche o formulário com esses dados — usuário revisa/edita livremente antes de clicar em "Salvar perfil" (que dispara o fluxo anterior).

Fluxo de dados — uso do perfil em Adaptar/ATS/Candidatar:
1. UI chama `BuscarPerfilEstruturado.executar(perfil_identificador)`.
2. Se existir, UI chama `MontarCurriculoDoPerfilEstruturado.executar(perfil_estruturado)`.
3. Se o resultado não for `None` (há conteúdo mínimo), a UI **não** pede upload de PDF — passa `curriculo_pre_montado=<Curriculo>` ao InputDto do use case correspondente, pulando a extração por IA.
4. Se o perfil não existir, ou `MontarCurriculoDoPerfilEstruturado` retornar `None` (sem conteúdo suficiente), a UI mantém o comportamento atual (upload de PDF / biblioteca), passando `pdf_curriculo=...`.

## Design de Implementação

### Interfaces Principais

```python
class PerfilEstruturadoRepository(ABC):
    @abstractmethod
    def salvar(self, perfil: PerfilEstruturado) -> PerfilEstruturado: ...

    @abstractmethod
    def buscar_por_perfil(self, perfil_identificador: str) -> PerfilEstruturado | None: ...
```

```python
class ExtratorPerfilEstruturadoPort(ABC):
    @abstractmethod
    def extrair(self, pdf_bytes: bytes) -> DadosPerfilExtraidos: ...
```

```python
class MontarCurriculoDoPerfilEstruturado:
    def executar(self, perfil: PerfilEstruturado) -> Curriculo | None:
        """Converte o perfil estruturado num Curriculo (mesmo agregado da Fase 0).

        Cada seção do Curriculo é montada concatenando as entradas estruturadas
        correspondentes em texto formatado (ex: cada ExperienciaProfissional vira
        um parágrafo "Cargo — Empresa (período)\\nDescrição"). Seções sem conteúdo
        são omitidas. Se nenhuma seção tiver conteúdo, retorna None (a UI então
        cai no fluxo de upload de PDF, como se o perfil não existisse).
        """
        ...
```

```python
class SalvarPerfilEstruturado:
    def __init__(self, repositorio: PerfilEstruturadoRepository) -> None: ...
    def executar(self, input_dto: SalvarPerfilEstruturadoInputDto) -> PerfilEstruturado: ...

class BuscarPerfilEstruturado:
    def __init__(self, repositorio: PerfilEstruturadoRepository) -> None: ...
    def executar(self, perfil_identificador: str) -> PerfilEstruturado | None: ...

class ImportarPerfilDePdf:
    def __init__(self, extrator: ExtratorPerfilEstruturadoPort) -> None: ...
    def executar(self, input_dto: ImportarPerfilDePdfInputDto) -> DadosPerfilExtraidos: ...
```

Alteração nos três use cases existentes (exemplo com `AdaptarCurriculoParaVagaInputDto`; o mesmo padrão vale para `AnalisarAtsVagaInputDto` e `CandidatarNaVagaExternaInputDto`):

```python
@dataclass(frozen=True)
class AdaptarCurriculoParaVagaInputDto:
    pdf_curriculo: bytes | None = None          # antes: bytes (obrigatório)
    curriculo_pre_montado: Curriculo | None = None  # novo
    descricao_vaga: str = ...
    # ... demais campos inalterados

# em use_case.py:
def executar(self, input_dto: ...) -> ...:
    ...
    curriculo_original = (
        input_dto.curriculo_pre_montado
        if input_dto.curriculo_pre_montado is not None
        else self._extrator.extrair(input_dto.pdf_curriculo)
    )
    ...
```

O validator passa a exigir "`pdf_curriculo` OU `curriculo_pre_montado`", em vez de só `pdf_curriculo`.

### Modelos de Dados

```python
class NivelIdioma(Enum):
    BASICO = auto()
    INTERMEDIARIO = auto()
    AVANCADO = auto()
    FLUENTE = auto()
    NATIVO = auto()

@dataclass(frozen=True)
class ExperienciaProfissional:
    empresa: str
    cargo: str
    periodo: str
    descricao: str

@dataclass(frozen=True)
class FormacaoAcademica:
    instituicao: str
    curso: str
    periodo: str

@dataclass(frozen=True)
class Certificacao:
    nome: str
    instituicao: str
    ano: str

@dataclass(frozen=True)
class Idioma:
    idioma: str
    nivel: NivelIdioma

@dataclass(frozen=True)
class DadosPerfilExtraidos:
    nome_completo: str
    email: str
    linkedin: str
    resumo_profissional: str
    experiencias: tuple[ExperienciaProfissional, ...]
    formacoes: tuple[FormacaoAcademica, ...]
    certificacoes: tuple[Certificacao, ...]
    idiomas: tuple[Idioma, ...]
    tecnologias: tuple[str, ...]

@dataclass(frozen=True)
class PerfilEstruturado:
    perfil_identificador: str
    nome_completo: str
    email: str
    linkedin: str
    resumo_profissional: str
    experiencias: tuple[ExperienciaProfissional, ...]
    formacoes: tuple[FormacaoAcademica, ...]
    certificacoes: tuple[Certificacao, ...]
    idiomas: tuple[Idioma, ...]
    tecnologias: tuple[str, ...]
```

Esquema SQLite (nova tabela, uma linha por perfil — upsert, sem histórico):

```sql
CREATE TABLE IF NOT EXISTS perfil_estruturado (
    perfil_identificador TEXT PRIMARY KEY,
    nome_completo TEXT NOT NULL,
    email TEXT NOT NULL,
    linkedin TEXT NOT NULL DEFAULT '',
    resumo_profissional TEXT NOT NULL DEFAULT '',
    experiencias_json TEXT NOT NULL DEFAULT '[]',
    formacoes_json TEXT NOT NULL DEFAULT '[]',
    certificacoes_json TEXT NOT NULL DEFAULT '[]',
    idiomas_json TEXT NOT NULL DEFAULT '[]',
    tecnologias_json TEXT NOT NULL DEFAULT '[]'
);
```

`PerfilEstruturadoRepositoryImpl.salvar` usa `INSERT ... ON CONFLICT(perfil_identificador) DO UPDATE` (upsert real, não "ler depois escrever"), serializando cada tupla de sub-entidades via `json.dumps([dataclasses.asdict(e) for e in ...])` e desserializando de volta na leitura.

### Endpoints de API

Não aplicável — tudo acionado pela UI Streamlit chamando os use cases diretamente.

## Abordagem de Testes

### Testes Unidade

- `PerfilEstruturado` e sub-entidades: validação de campos obrigatórios (nome, email).
- `MontarCurriculoDoPerfilEstruturado`: perfil completo gera `Curriculo` com todas as seções; perfil parcial (só algumas seções) gera `Curriculo` só com as seções presentes; perfil sem nenhum conteúdo retorna `None`.
- `PerfilEstruturadoRepositoryImpl`: salvar e buscar (round-trip incluindo listas vazias e múltiplas entradas); salvar duas vezes para o mesmo `perfil_identificador` sobrescreve (upsert), sem duplicar linha.
- `SalvarPerfilEstruturado`, `BuscarPerfilEstruturado`: com fake do repositório.
- `ImportarPerfilDePdf`: com fake de `ExtratorPerfilEstruturadoPort`.
- `ExtratorPerfilEstruturadoGroq`: com fake de `ClienteGroq` (mesmo padrão dos demais adapters Groq), incluindo o caso de resposta com campos ausentes/malformados (mesma robustez já aplicada aos outros adapters Groq nesta base de código — nunca deixar `.strip()` quebrar em um valor não-string).
- `AdaptarCurriculoParaVaga`, `AnalisarAtsVaga`, `CandidatarNaVagaExterna`: novo teste em cada um confirmando que, com `curriculo_pre_montado` informado, o extrator (`ExtratorCurriculoPort`) NUNCA é chamado; testes existentes (via `pdf_curriculo`) continuam passando sem alteração.

### Testes de Serviço

Não aplicável (sem endpoints HTTP novos).

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Domínio: `PerfilEstruturado` + sub-entidades + `DadosPerfilExtraidos` + porta de repositório — sem dependências.
2. Persistência: schema + `PerfilEstruturadoRepositoryImpl`, com testes de integração.
3. `MontarCurriculoDoPerfilEstruturado` (Domain Service), com testes.
4. Use cases `SalvarPerfilEstruturado` e `BuscarPerfilEstruturado`, com testes.
5. Porta `ExtratorPerfilEstruturadoPort` + adapter `ExtratorPerfilEstruturadoGroq` + use case `ImportarPerfilDePdf`, com testes.
6. Estender os três use cases existentes com `curriculo_pre_montado`, com testes de regressão.
7. UI: página "Meu Perfil" (formulário + import de PDF + salvar).
8. UI: integrar perfil como fonte padrão em "Adaptar Currículo", "Analisar ATS" e "Candidatar" (Vagas), com fallback para upload de PDF.
9. Validação manual end-to-end + suíte completa de testes.

### Dependências Técnicas

- Nenhuma dependência nova de terceiros — reaproveita `groq`, `pdfplumber` (via `ExtratorTextoPdfPlumber`) e `streamlit`, já presentes.
- Depende de `Curriculo`/`SecaoCurriculo` (domínio, Fase 0), `GeradorPdfPort`/`AjustadorTextoPort`/`GerarCartaApresentacaoPort` (Fases 0-1), e dos três use cases existentes que serão estendidos (Fases 0-3).

## Monitoramento e Observabilidade

- Nenhum log adicional além do já existente nos adapters Groq reaproveitados.

## Considerações Técnicas

### Decisões Principais

- **`periodo` como texto livre, não datas estruturadas**: simplifica a UX (usuário raramente sabe o dia exato de início/fim de uma experiência) e o código (sem parsing/validação de datas parciais). Ainda assim atende à decisão confirmada no PRD de "campos estruturados" — empresa, cargo, período e descrição continuam sendo campos distintos, só o período em si não é subdividido.
- **`MontarCurriculoDoPerfilEstruturado` retorna `None` quando não há conteúdo mínimo**, em vez de lançar exceção ou retornar um `Curriculo` vazio — permite que a UI trate isso de forma simples e uniforme: "se `None`, é como se o perfil não existisse, cai no fluxo de upload de PDF já existente e testado".
- **`curriculo_pre_montado` opcional no InputDto dos três use cases existentes**, em vez de criar três novos use cases paralelos ("AdaptarCurriculoDoPerfil", etc.) — evita duplicar toda a lógica de adaptação/análise/candidatura já madura; a mudança é mínima e cirúrgica (uma condicional no início de cada `executar`).
- **Persistência como upsert de linha única (sem histórico)**: decisão confirmada no PRD — simplicidade sobre versionamento, consistente com o restante do sistema (`CurriculoSalvo` da Fase 0 também não versiona).
- **Extração direta PDF → JSON estruturado** (novo prompt) em vez de tentar reaproveitar o texto livre já segmentado por `ExtratorCurriculoSegmentadoPorIA` e parsear de novo — um único prompt bem desenhado que já pede a estrutura final é mais simples e confiável do que fazer parsing de texto livre em cima de outro texto livre.

### Riscos Conhecidos

- A extração estruturada por IA (`ExtratorPerfilEstruturadoGroq`) pode não separar corretamente experiências em entradas distintas quando o formato do PDF de origem for muito incomum (ex: currículos em formato de tabela, ou o PDF exportado do LinkedIn com layout diferente do currículo "tradicional") — mitigação: dados sempre editáveis antes de salvar, nunca persistidos automaticamente (já é requisito do PRD).
- Chamada de IA adicional (uma a mais) apenas no fluxo de *importar* de PDF — não afeta o custo de Adaptar/ATS/Candidatar, que na verdade **diminui** uma chamada de IA (a extração) quando o perfil já existe.
- Migração implícita: usuários que já têm currículos na biblioteca (Fase 0) continuam sem perfil estruturado até importarem ou preencherem manualmente — não há migração automática nesta fase (fora de escopo, conforme PRD).

### Conformidade com Padrões

Segue `.windsurf/rules/code-design-standards.md`: porta e Domain Service co-localizados em `domain.perfil_estruturado`; use cases como pacotes (`dtos.py`/`use_case.py`/`validator.py`/`__init__.py`, exceto `BuscarPerfilEstruturado` que segue o padrão "sem DTO" já usado em `EntrarOuCriarPerfil`); nenhum use case chama outro use case diretamente.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/plataforma-base/job-0009-perfil-estruturado-curriculo-mestre/prd-job-0009.md`
- `src/domain/perfil_estruturado/__init__.py` (novo — `PerfilEstruturado`, `DadosPerfilExtraidos`, `ExperienciaProfissional`, `FormacaoAcademica`, `Certificacao`, `Idioma`, `NivelIdioma`)
- `src/domain/perfil_estruturado/perfil_estruturado_repository.py` (novo)
- `src/domain/perfil_estruturado/extrator_perfil_estruturado_port.py` (novo)
- `src/domain/perfil_estruturado/montar_curriculo_do_perfil_estruturado_service.py` (novo, Domain Service)
- `src/infrastructure/persistence/perfil_estruturado_repository_impl.py` (novo)
- `src/infrastructure/persistence/_conexao_sqlite.py` (modificado — nova tabela no `_SCHEMA`)
- `src/infrastructure/llm/extrator_perfil_estruturado_groq.py` (novo)
- `src/application/use_cases/salvar_perfil_estruturado/{dtos,use_case,validator,__init__}.py` (novo)
- `src/application/use_cases/buscar_perfil_estruturado/{use_case,__init__}.py` (novo, sem DTO)
- `src/application/use_cases/importar_perfil_de_pdf/{dtos,use_case,validator,__init__}.py` (novo)
- `src/application/use_cases/adaptar_curriculo_para_vaga/{dtos,use_case,validator}.py` (modificado — `curriculo_pre_montado`)
- `src/application/use_cases/analisar_ats_vaga/{dtos,use_case,validator}.py` (modificado — `curriculo_pre_montado`)
- `src/application/use_cases/candidatar_na_vaga_externa/{dtos,use_case,validator}.py` (modificado — `curriculo_pre_montado`)
- `src/ui/app_streamlit.py` (modificado — nova página "Meu Perfil"; integração nas três páginas existentes)
- `src/tests/domain/perfil_estruturado/`, `src/tests/application/use_cases/salvar_perfil_estruturado/`, `.../buscar_perfil_estruturado/`, `.../importar_perfil_de_pdf/`, `src/tests/infrastructure/persistence/test_perfil_estruturado_repository_impl.py`, `src/tests/infrastructure/llm/test_extrator_perfil_estruturado_groq.py` (novos)

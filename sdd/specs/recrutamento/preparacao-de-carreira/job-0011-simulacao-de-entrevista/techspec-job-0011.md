# Especificação Técnica

> Nota: esta TechSpec nasceu de uma divisão do antigo `job-0008` (Simulação de Entrevista + Analytics). Cobre exclusivamente a Simulação de Entrevista; Analytics virou `job-0012`. Os caminhos abaixo já refletem a convenção `src/domain`/`src/application`/`src/infrastructure`/`src/ui` (Ports and Adapters, portas co-localizadas em `domain.<agregado>`, use cases como pacotes `dtos.py`/`use_case.py`/`validator.py`/`__init__.py`) adotada a partir da Fase 3.

## Resumo Executivo

Geração de roteiro de perguntas de entrevista via IA, a partir do currículo e da análise de vaga já associados a uma candidatura existente no Kanban (Fase 2). Segue o mesmo padrão de porta+adapter Groq já estabelecido em `GerarCartaApresentacaoPort`/`GeradorCartaApresentacaoGroq` (Fase 1). Não introduz nova persistência — reconstitui `Curriculo` e `AnaliseVaga` sob demanda a partir dos dados já salvos (PDF do currículo, texto da vaga).

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `RoteiroEntrevista` (novo, `src/domain/roteiro_entrevista/__init__.py`): value object — `perguntas_tecnicas: tuple[str, ...]`, `perguntas_comportamentais: tuple[str, ...]`.
- `GeradorRoteiroEntrevistaPort` (novo, `src/domain/roteiro_entrevista/gerador_roteiro_entrevista_port.py`): porta — `gerar(curriculo: Curriculo, analise_vaga: AnaliseVaga) -> RoteiroEntrevista`.
- `GeradorRoteiroEntrevistaGroq` (novo, `src/infrastructure/llm/gerador_roteiro_entrevista_groq.py`): implementação via `ClienteGroq` já existente, mesmo padrão de robustez a respostas malformadas já usado nos demais adapters Groq do projeto (`str(valor).strip() if valor else ""`, nunca deixar `.strip()` quebrar em tipo inesperado).
- `GerarRoteiroEntrevista` (novo use case, `src/application/use_cases/gerar_roteiro_entrevista/`): recebe o PDF do currículo e o texto da vaga já resolvidos pela UI (não um `candidatura_id` — ver "Decisões Principais"), reaproveita `ExtratorCurriculoPort` e `JobDescriptionAnalyzerPort` (Fase 0/1) para reconstituir `Curriculo`/`AnaliseVaga`, e chama `GeradorRoteiroEntrevistaPort`.
- `src/ui/app_streamlit.py` (modificado): ganha botão "Gerar roteiro de entrevista" no detalhe de cada candidatura, na página "Vagas & Candidaturas" (Fase 2) já existente.

Fluxo de dados:
1. UI (na renderização do Kanban) já tem a `Candidatura` selecionada; resolve `Vaga.texto_descricao` (via `vaga_id`) e `CurriculoSalvo.pdf_bytes` (via `curriculo_salvo_id`) — ver "Riscos Conhecidos" sobre a necessidade de `buscar_por_id` nesses repositórios.
2. UI chama `GerarRoteiroEntrevista.executar(GerarRoteiroEntrevistaInputDto(pdf_curriculo=..., descricao_vaga=...))`.
3. Use case chama `ExtratorCurriculoPort.extrair()` e `JobDescriptionAnalyzerPort.analisar()` (portas já existentes, sem alteração).
4. Use case chama `GeradorRoteiroEntrevistaPort.gerar(curriculo, analise_vaga)` → `RoteiroEntrevista`.
5. UI renderiza as perguntas por categoria.

## Design de Implementação

### Interfaces Principais

```python
class GeradorRoteiroEntrevistaPort(ABC):
    @abstractmethod
    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga) -> RoteiroEntrevista: ...
```

```python
class GerarRoteiroEntrevista:
    def __init__(
        self,
        extrator: ExtratorCurriculoPort,
        analisador_vaga: JobDescriptionAnalyzerPort,
        gerador_roteiro: GeradorRoteiroEntrevistaPort,
    ) -> None: ...

    def executar(self, input_dto: GerarRoteiroEntrevistaInputDto) -> RoteiroEntrevista: ...
```

```python
@dataclass(frozen=True)
class GerarRoteiroEntrevistaInputDto:
    pdf_curriculo: bytes
    descricao_vaga: str
```

Nota: recebe `pdf_curriculo`/`descricao_vaga` diretamente, não um `candidatura_id` — mesmo padrão já usado em `AnalisarAtsVaga`/`AdaptarCurriculoParaVaga` (a UI resolve os dados antes de chamar o use case, que não conhece `Candidatura`/`Vaga`/`CurriculoSalvo` como conceitos, evitando acoplar este use case às portas de persistência do Kanban).

### Modelos de Dados

```python
@dataclass(frozen=True)
class RoteiroEntrevista:
    perguntas_tecnicas: tuple[str, ...]
    perguntas_comportamentais: tuple[str, ...]
```

Não há novo esquema SQLite — nada é persistido nesta fase (o roteiro é gerado e exibido, não salvo).

### Endpoints de API

Não aplicável — mesmo modelo monolítico Streamlit.

## Pontos de Integração

- `src/domain/curriculo/extrator_curriculo_port.py` (existente, Fase 0): reaproveitado sem alteração.
- `src/domain/vaga/job_description_analyzer_port.py` (existente, Fase 1): reaproveitado sem alteração.
- `src/domain/candidatura/candidatura_repository.py`, `src/domain/vaga/vaga_repository.py`, `src/domain/curriculo_salvo/curriculo_salvo_repository.py` (existentes, Fase 0/2): nenhum tem hoje um método `buscar_por_id` — só listagens (`listar_por_perfil`, `listar_nao_convertidas`). Ver "Riscos Conhecidos".

## Abordagem de Testes

### Testes Unidade

- `GerarRoteiroEntrevista`: usando fakes de `ExtratorCurriculoPort`, `JobDescriptionAnalyzerPort` e `GeradorRoteiroEntrevistaPort`, validando que o currículo e a análise de vaga são corretamente repassados à porta de geração.
- `GeradorRoteiroEntrevistaGroq`: mesmo padrão de `src/tests/infrastructure/llm/test_gerador_carta_apresentacao_groq.py` — prompt inclui currículo e análise de vaga; resposta malformada não quebra (campos ausentes viram tupla vazia, não exceção).

### Testes de Serviço

Não aplicável (sem endpoints HTTP novos).

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. `RoteiroEntrevista` (domain) + `GeradorRoteiroEntrevistaPort`, sem dependências.
2. `GeradorRoteiroEntrevistaGroq` (infra), com testes.
3. Resolver o gap de acesso a dados (ver "Riscos Conhecidos"): adicionar `buscar_por_id` a `VagaRepository` e `CurriculoSalvoRepository` (e respectivos `*RepositoryImpl`), com testes de integração.
4. `GerarRoteiroEntrevista` (use case), com testes usando fakes.
5. Integração na UI: botão de gerar roteiro no detalhe da candidatura (Fase 2), usando os métodos `buscar_por_id` do passo 3 para resolver `Vaga`/`CurriculoSalvo` a partir da `Candidatura` selecionada.
6. Validação manual com uma candidatura real do Kanban.

### Dependências Técnicas

- Nenhuma biblioteca nova — reaproveita `groq` já presente no projeto.
- Depende da Fase 0 (currículos salvos), Fase 1 (padrão de porta/adapter Groq) e Fase 2 (Kanban de candidaturas) já implementadas.

## Monitoramento e Observabilidade

- Logar (INFO) cada geração de roteiro de entrevista (sem logar o conteúdo do currículo).
- Logar (ERROR) falhas na chamada Groq para geração de roteiro, com fallback de mensagem amigável na UI.

## Considerações Técnicas

### Decisões Principais

- `GerarRoteiroEntrevista` recebe `pdf_curriculo`/`descricao_vaga` diretamente, não um `candidatura_id`: mantém o use case desacoplado das portas de persistência do Kanban (Fase 2), consistente com o padrão já usado em `AnalisarAtsVaga`/`AdaptarCurriculoParaVaga`/`CandidatarNaVagaExterna`.
- Reconstituir `AnaliseVaga` e `Curriculo` sob demanda a partir dos dados salvos, em vez de persistir esses objetos já processados: evita duplicar dados e mantém `Vaga`/`CurriculoSalvo` como fonte única de verdade, ao custo de reprocessar (chamada Groq) a cada geração de roteiro — aceitável dado que roteiros não são gerados com alta frequência.

### Riscos Conhecidos

- **Gap de acesso a dados**: nem `VagaRepository` nem `CurriculoSalvoRepository` têm hoje um método `buscar_por_id` — só listagens. A UI precisa resolver `Candidatura.vaga_id`/`curriculo_salvo_id` para os objetos completos antes de chamar o use case. Mitigação: adicionar `buscar_por_id` a ambas as portas (extensão aditiva, não quebra nada existente) como parte da Tarefa 3 desta fase.
- Reprocessar currículo e vaga via IA a cada geração de roteiro tem custo de latência e de API — se o uso crescer, vale considerar cache do resultado por candidatura (fora de escopo desta fase).

### Conformidade com Padrões

Segue `.windsurf/rules/code-design-standards.md`: porta co-localizada em `domain.roteiro_entrevista`; use case como pacote (`dtos.py`/`use_case.py`/`validator.py`/`__init__.py`); não chama nenhum outro use case.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/preparacao-de-carreira/job-0011-simulacao-de-entrevista/prd-job-0011.md`
- `src/domain/roteiro_entrevista/__init__.py` (novo)
- `src/domain/roteiro_entrevista/gerador_roteiro_entrevista_port.py` (novo)
- `src/infrastructure/llm/gerador_roteiro_entrevista_groq.py` (novo)
- `src/application/use_cases/gerar_roteiro_entrevista/{dtos,use_case,validator,__init__}.py` (novo)
- `src/domain/vaga/vaga_repository.py`, `src/domain/curriculo_salvo/curriculo_salvo_repository.py` (modificados — novo método `buscar_por_id`)
- `src/infrastructure/persistence/vaga_repository_impl.py`, `src/infrastructure/persistence/curriculo_salvo_repository_impl.py` (modificados)
- `src/ui/app_streamlit.py` (modificado)
- `src/tests/domain/roteiro_entrevista/`, `src/tests/application/use_cases/gerar_roteiro_entrevista/`, `src/tests/infrastructure/llm/test_gerador_roteiro_entrevista_groq.py` (novos)

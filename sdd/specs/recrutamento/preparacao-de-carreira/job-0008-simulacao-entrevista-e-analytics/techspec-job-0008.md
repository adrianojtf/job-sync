# Especificação Técnica

## Resumo Executivo

Esta Tech Spec cobre as duas funcionalidades finais do roadmap, conforme `prd-job-0008.md`: geração de roteiro de perguntas de entrevista via IA, e um dashboard de analytics agregando dados já persistidos pelo Kanban (Fase 2, `job-0006`). A geração de perguntas segue o mesmo padrão de porta+adapter Groq já estabelecido em `GeradorCartaApresentacaoPort`/`GeradorCartaApresentacaoGroq` (Fase 1). O dashboard não introduz nova persistência — é uma camada de agregação (SQL de leitura) sobre as tabelas `candidatura` e `curriculo_salvo` já existentes.

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `GeradorRoteiroEntrevistaPort` (novo, `application/ports/gerador_roteiro_entrevista_port.py`): interface para gerar perguntas a partir de currículo + análise de vaga.
- `GeradorRoteiroEntrevistaGroq` (novo, `infrastructure/llm/gerador_roteiro_entrevista_groq.py`): implementação usando o `ClienteGroq` já existente, mesmo padrão de `GeradorCartaApresentacaoGroq`.
- `RoteiroEntrevista` (novo, `domain/roteiro_entrevista.py`): value object com `perguntas_tecnicas: tuple[str, ...]` e `perguntas_comportamentais: tuple[str, ...]`.
- `GerarRoteiroEntrevista` (novo use case, `application/use_cases/gerar_roteiro_entrevista.py`): recebe `candidatura_id`, busca a `Candidatura` (Fase 2) e a `Vaga`/`CurriculoSalvo` associados, monta `AnaliseVaga` e `Curriculo` (reaproveitando `JobDescriptionAnalyzerPort` e `ExtratorCurriculoPort`), chama a porta acima.
- `RepositorioAnalyticsPort` (novo, `application/ports/repositorio_analytics_port.py`): interface de leitura agregada — não é um repositório de escrita, apenas consultas sobre dados já existentes.
- `RepositorioAnalyticsSqlite` (novo, `infrastructure/persistence/repositorio_analytics_sqlite.py`): implementação com queries SQL de agregação sobre as tabelas `candidatura` (Fase 2) e `curriculo_salvo` (Fase 0), reaproveitando a mesma conexão SQLite.
- `ObterDashboardPessoal` (novo use case, `application/use_cases/obter_dashboard_pessoal.py`): orquestra a chamada a `RepositorioAnalyticsPort` e monta o objeto `DashboardPessoal`.
- `ui/app_streamlit.py` (modificado): ganha botão "Gerar roteiro de entrevista" no detalhe da candidatura (Fase 2), e uma nova aba "Meu desempenho" exibindo o dashboard.

Fluxo de dados — roteiro de entrevista:
1. UI chama `GerarRoteiroEntrevista.executar(candidatura_id)`.
2. Use case busca `Candidatura` → `Vaga` associada → `CurriculoSalvo` associado (todos via portas já existentes das Fases 0 e 2).
3. Reaproveita `JobDescriptionAnalyzerPort.analisar()` sobre `Vaga.texto_descricao` e `ExtratorCurriculoPort.extrair()` sobre `CurriculoSalvo.pdf_bytes`.
4. Chama `GeradorRoteiroEntrevistaPort.gerar(curriculo, analise_vaga)` → `RoteiroEntrevista`.

Fluxo de dados — dashboard:
1. UI chama `ObterDashboardPessoal.executar(perfil_identificador)`.
2. Use case chama `RepositorioAnalyticsPort` para: contagem por status, taxa de avanço geral, taxa de avanço por `curriculo_salvo_id`.
3. UI renderiza os números/tabelas retornados.

## Design de Implementação

### Interfaces Principais

```python
class GeradorRoteiroEntrevistaPort(ABC):
    @abstractmethod
    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga) -> RoteiroEntrevista: ...
```

```python
class RepositorioAnalyticsPort(ABC):
    @abstractmethod
    def contar_por_status(self, perfil_identificador: str) -> dict[StatusCandidatura, int]: ...

    @abstractmethod
    def taxa_avanco_geral(self, perfil_identificador: str) -> float: ...

    @abstractmethod
    def taxa_avanco_por_curriculo(self, perfil_identificador: str) -> dict[str, float]: ...
```

### Modelos de Dados

```python
@dataclass(frozen=True)
class RoteiroEntrevista:
    perguntas_tecnicas: tuple[str, ...]
    perguntas_comportamentais: tuple[str, ...]

@dataclass(frozen=True)
class DashboardPessoal:
    contagem_por_status: dict[StatusCandidatura, int]
    taxa_avanco_geral: float
    taxa_avanco_por_curriculo: dict[str, float]  # chave: nome_referencia do CurriculoSalvo
```

Não há novo esquema SQLite — todas as consultas são `SELECT` sobre `candidatura` e `curriculo_salvo` (Fase 2/0). "Avanço" é definido como `status != StatusCandidatura.APLICADO` no momento da consulta (dado que não há histórico de trânsito detalhado por timestamp além da mudança de status mais recente, conforme modelo já definido na Fase 2).

### Endpoints de API

Não aplicável — mesmo modelo monolítico Streamlit.

## Pontos de Integração

- `application/ports/job_description_analyzer_port.py` (existente): reaproveitado sem alteração para reconstituir `AnaliseVaga` a partir do texto salvo em `Vaga.texto_descricao`.
- `application/ports/extrator_curriculo_port.py` (existente): reaproveitado sem alteração para reconstituir `Curriculo` a partir do `CurriculoSalvo.pdf_bytes`.
- `infrastructure/persistence/repositorio_sqlite.py` (Fase 0/2): a nova classe `RepositorioAnalyticsSqlite` compartilha a mesma conexão/arquivo, mas fica em módulo separado por ser puramente leitura/agregação, não escrita transacional — evita misturar responsabilidades de CRUD com relatório na mesma classe.

## Abordagem de Testes

### Testes Unidade

- `GerarRoteiroEntrevista`: usando fake de `GeradorRoteiroEntrevistaPort`, validando que candidatura/vaga/currículo são corretamente combinados antes da chamada à porta.
- `GeradorRoteiroEntrevistaGroq`: seguindo o padrão de `tests/infrastructure/llm/test_ajustador_texto_groq.py`, validando que o prompt inclui tanto a análise de vaga quanto o currículo.
- `ObterDashboardPessoal`: usando fake de `RepositorioAnalyticsPort`, validando a montagem do `DashboardPessoal`.

### Testes de Serviço

- `RepositorioAnalyticsSqlite`: teste de integração com banco SQLite temporário pré-populado com candidaturas em diferentes status e currículos, validando contagens e taxas de avanço calculadas corretamente, incluindo o caso de zero candidaturas (sem divisão por zero).

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. `RoteiroEntrevista` (domain) + `GeradorRoteiroEntrevistaPort` + `GeradorRoteiroEntrevistaGroq`, com testes — depende apenas de portas já existentes das fases anteriores.
2. `GerarRoteiroEntrevista` (use case), com testes usando fakes.
3. Integração na UI: botão de gerar roteiro no detalhe da candidatura (Fase 2).
4. `DashboardPessoal` (domain) + `RepositorioAnalyticsPort` + `RepositorioAnalyticsSqlite`, com testes de integração cobrindo o caso de zero dados.
5. `ObterDashboardPessoal` (use case), com testes usando fake.
6. Integração na UI: nova aba "Meu desempenho".
7. Validação manual com um perfil de teste tendo candidaturas em múltiplos status e currículos.

### Dependências Técnicas

- Nenhuma biblioteca nova — reaproveita `groq` e `sqlite3` já presentes no projeto após as fases anteriores.
- Depende da Fase 0 (currículos salvos), Fase 1 (padrão de porta/adapter Groq para geração de texto) e Fase 2 (Kanban de candidaturas) já implementadas — esta é a fase com mais dependências acumuladas do roadmap.

## Monitoramento e Observabilidade

- Logar (INFO) cada geração de roteiro de entrevista (candidatura_id, sem logar o conteúdo do currículo).
- Logar (ERROR) falhas na chamada Groq para geração de roteiro, com fallback de mensagem amigável na UI.
- Logar (WARNING) quando o dashboard for consultado com zero candidaturas no perfil, para diferenciar de um erro de cálculo.

## Considerações Técnicas

### Decisões Principais

- Reconstituir `AnaliseVaga` e `Curriculo` sob demanda a partir dos dados salvos (texto da vaga, PDF do currículo) em vez de persistir esses objetos já processados: evita duplicar dados e mantém `Vaga`/`CurriculoSalvo` como fonte única de verdade, ao custo de reprocessar (chamada Groq) a cada geração de roteiro — aceitável dado que roteiros não são gerados com alta frequência.
- "Taxa de avanço" definida como status atual diferente de `APLICADO`, não como histórico de trânsito completo: o modelo de dados da Fase 2 já registra `historico_status`, mas usar apenas o status atual é suficiente para as métricas definidas neste PRD e evita lógica de agregação temporal mais complexa.
- `RepositorioAnalyticsSqlite` separado do `RepositorioSqlite` principal: mantém queries de relatório (potencialmente mais pesadas, com `GROUP BY`) isoladas das operações transacionais de CRUD.

### Riscos Conhecidos

- Reprocessar currículo e vaga via IA a cada geração de roteiro tem custo de latência e de API — se o uso crescer, vale considerar cache do resultado por candidatura (fora de escopo desta fase).
- Taxa de avanço por currículo pode ser enganosa com poucas amostras (ex: 1 candidatura com um currículo, que avançou, mostra 100%) — o PRD já registra isso como questão em aberto de produto; a implementação deve permitir fácil ajuste do limiar mínimo depois.

### Conformidade com Padrões

Não há regras em `.windsurf/rules` no repositório (diretório inexistente) — nenhum desvio a documentar. Mantém a Arquitetura Hexagonal: lógica de agregação em `RepositorioAnalyticsSqlite` (infraestrutura), sem regra de negócio de domínio embutida em SQL além de contagem/proporção simples.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/preparacao-de-carreira/job-0008-simulacao-entrevista-e-analytics/prd-job-0008.md`
- `domain/roteiro_entrevista.py`, `domain/dashboard_pessoal.py` (novos)
- `application/ports/gerador_roteiro_entrevista_port.py`, `application/ports/repositorio_analytics_port.py` (novos)
- `application/use_cases/gerar_roteiro_entrevista.py`, `application/use_cases/obter_dashboard_pessoal.py` (novos)
- `infrastructure/llm/gerador_roteiro_entrevista_groq.py` (novo)
- `infrastructure/persistence/repositorio_analytics_sqlite.py` (novo)
- `application/ports/job_description_analyzer_port.py`, `application/ports/extrator_curriculo_port.py` (existentes — reaproveitados)
- `ui/app_streamlit.py` (modificado)

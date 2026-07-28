# Especificação Técnica

> Nota: esta TechSpec nasceu de uma divisão do antigo `job-0008` (Simulação de Entrevista + Analytics). Cobre exclusivamente o Analytics de Desempenho; Simulação de Entrevista virou `job-0011`. Os caminhos abaixo já refletem a convenção `src/domain`/`src/application`/`src/infrastructure`/`src/ui` adotada a partir da Fase 3.

## Resumo Executivo

Dashboard pessoal ("Meu Desempenho") agregando dados já persistidos pelo Kanban de candidaturas (Fase 2, `job-0006`). Não introduz nova persistência — é uma camada de leitura/agregação (SQL `GROUP BY`/contagem) sobre as tabelas `candidatura` e `curriculo_salvo` já existentes, isolada num repositório próprio para não misturar consultas de relatório com as operações transacionais de CRUD do Kanban.

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `DashboardPessoal` (novo, `src/domain/dashboard_pessoal/__init__.py`): value object — `contagem_por_status: dict[StatusCandidatura, int]`, `taxa_avanco_geral: float`, `taxa_avanco_por_curriculo: dict[str, float]` (chave: `nome_referencia` do `CurriculoSalvo`).
- `DashboardPessoalRepository` (novo, `src/domain/dashboard_pessoal/dashboard_pessoal_repository.py`): porta — `obter_dashboard(perfil_identificador: str) -> DashboardPessoal`.
- `DashboardPessoalRepositoryImpl` (novo, `src/infrastructure/persistence/dashboard_pessoal_repository_impl.py`): implementação com queries SQL de agregação sobre `candidatura` (Fase 2) e `curriculo_salvo` (Fase 0), reaproveitando `criar_conexao` já existente.
- `ObterDashboardPessoal` (novo use case, `src/application/use_cases/obter_dashboard_pessoal/`, sem DTO — mesmo padrão de `BuscarPerfilEstruturado`): `executar(perfil_identificador: str) -> DashboardPessoal`.
- `src/ui/app_streamlit.py` (modificado): nova página "Meu Desempenho" no menu lateral.

Fluxo de dados:
1. UI chama `ObterDashboardPessoal.executar(perfil_identificador)`.
2. Use case delega diretamente a `DashboardPessoalRepository.obter_dashboard(perfil_identificador)`.
3. UI renderiza contagem por status (`st.metric` por coluna do Kanban), taxa de avanço geral, e taxa de avanço por currículo (tabela ou gráfico de barras simples).

## Design de Implementação

### Interfaces Principais

```python
class DashboardPessoalRepository(ABC):
    @abstractmethod
    def obter_dashboard(self, perfil_identificador: str) -> DashboardPessoal: ...
```

```python
class ObterDashboardPessoal:
    def __init__(self, repositorio: DashboardPessoalRepository) -> None: ...
    def executar(self, perfil_identificador: str) -> DashboardPessoal: ...
```

### Modelos de Dados

```python
@dataclass(frozen=True)
class DashboardPessoal:
    contagem_por_status: dict[StatusCandidatura, int]
    taxa_avanco_geral: float
    taxa_avanco_por_curriculo: dict[str, float]
```

Não há novo esquema SQLite — todas as consultas são `SELECT`/`GROUP BY` sobre `candidatura` e `curriculo_salvo` (Fase 2/0), já existentes. "Avanço" é definido como `status != StatusCandidatura.APLICADO` no momento da consulta (dado que o modelo da Fase 2 só guarda a mudança de status mais recente, não um histórico completo de trânsito por timestamp).

Com zero candidaturas no perfil, `taxa_avanco_geral` e cada entrada de `taxa_avanco_por_curriculo` devem retornar `0.0` (nunca dividir por zero).

### Endpoints de API

Não aplicável — mesmo modelo monolítico Streamlit.

## Pontos de Integração

- `src/infrastructure/persistence/_conexao_sqlite.py` (existente): `DashboardPessoalRepositoryImpl` reaproveita `criar_conexao` — nenhuma alteração de schema necessária.
- `src/domain/candidatura/__init__.py`, `src/domain/curriculo_salvo/__init__.py` (existentes): `StatusCandidatura` e `CurriculoSalvo` reaproveitados sem alteração.

## Abordagem de Testes

### Testes Unidade

- `ObterDashboardPessoal`: usando fake de `DashboardPessoalRepository`, validando que o use case repassa o resultado sem alteração.

### Testes de Serviço

- `DashboardPessoalRepositoryImpl`: teste de integração com banco SQLite temporário pré-populado com candidaturas em diferentes status e currículos, validando:
  - Contagem por status correta.
  - Taxa de avanço geral correta.
  - Taxa de avanço por currículo correta, incluindo isolamento entre currículos diferentes.
  - Caso de zero candidaturas no perfil (sem `ZeroDivisionError`, retorna `0.0`).

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. `DashboardPessoal` (domain) + `DashboardPessoalRepository` (porta), sem dependências.
2. `DashboardPessoalRepositoryImpl` (infra), com testes de integração cobrindo o caso de zero dados.
3. `ObterDashboardPessoal` (use case), com testes usando fake.
4. Integração na UI: nova página "Meu Desempenho" no menu lateral.
5. Validação manual com um perfil de teste tendo candidaturas em múltiplos status e currículos.

### Dependências Técnicas

- Nenhuma biblioteca nova — reaproveita `sqlite3` já presente no projeto.
- Depende da Fase 0 (currículos salvos) e Fase 2 (Kanban de candidaturas) já implementadas.

## Monitoramento e Observabilidade

- Logar (WARNING) quando o dashboard for consultado com zero candidaturas no perfil, para diferenciar de um erro de cálculo.

## Considerações Técnicas

### Decisões Principais

- "Taxa de avanço" definida como status atual diferente de `APLICADO`, não como histórico de trânsito completo: o modelo de dados da Fase 2 já registra `historico_status`, mas usar apenas o status atual é suficiente para as métricas definidas no PRD e evita lógica de agregação temporal mais complexa.
- `DashboardPessoalRepositoryImpl` separado dos demais `*RepositoryImpl` (não estende `CandidaturaRepositoryImpl`): mantém queries de relatório (potencialmente mais pesadas, com `GROUP BY`) isoladas das operações transacionais de CRUD, e evita a colisão de nomes de método entre portas já documentada no projeto (`_conexao_sqlite.py`).
- `ObterDashboardPessoal` delega inteiramente ao repositório (sem lógica própria) — a agregação em si já é responsabilidade do `DashboardPessoalRepositoryImpl`, mantendo o use case como uma fina camada de orquestração, mesmo padrão de `BuscarPerfilEstruturado`.

### Riscos Conhecidos

- Taxa de avanço por currículo pode ser enganosa com poucas amostras (ex: 1 candidatura com um currículo, que avançou, mostra 100%) — o PRD já registra isso como questão em aberto de produto; a implementação deve permitir fácil ajuste de um limiar mínimo depois (ex: esconder a métrica com menos de 3 candidaturas daquele currículo).

### Conformidade com Padrões

Segue `.windsurf/rules/code-design-standards.md`: porta co-localizada em `domain.dashboard_pessoal`, nomeada `DashboardPessoalRepository` (padrão `<Agregado>Repository`); use case sem DTO (mesmo padrão de `BuscarPerfilEstruturado`); não chama nenhum outro use case. Mantém a Arquitetura Hexagonal: lógica de agregação em `DashboardPessoalRepositoryImpl` (infraestrutura), sem regra de negócio de domínio embutida em SQL além de contagem/proporção simples.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/preparacao-de-carreira/job-0012-analytics-de-desempenho/prd-job-0012.md`
- `src/domain/dashboard_pessoal/__init__.py` (novo)
- `src/domain/dashboard_pessoal/dashboard_pessoal_repository.py` (novo)
- `src/infrastructure/persistence/dashboard_pessoal_repository_impl.py` (novo)
- `src/application/use_cases/obter_dashboard_pessoal/{use_case,__init__}.py` (novo, sem DTO)
- `src/domain/candidatura/__init__.py`, `src/domain/curriculo_salvo/__init__.py` (existentes — reaproveitados sem alteração)
- `src/ui/app_streamlit.py` (modificado)
- `src/tests/domain/dashboard_pessoal/`, `src/tests/application/use_cases/obter_dashboard_pessoal/`, `src/tests/infrastructure/persistence/test_dashboard_pessoal_repository_impl.py` (novos)

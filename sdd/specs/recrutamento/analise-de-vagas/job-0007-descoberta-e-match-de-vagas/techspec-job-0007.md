# Especificação Técnica

## Resumo Executivo

Esta Tech Spec descreve a implementação da busca de vagas em fontes externas e do cálculo de match, conforme `prd-job-0007.md`. A abordagem introduz uma porta única `BuscadorVagasExternoPort` com cinco adapters (RemoteOK, We Work Remotely, Arbeitnow, Adzuna, Google Custom Search), consultados em paralelo com timeout individual. O adapter do Google Custom Search tem uma responsabilidade extra em relação aos demais: como a API só devolve link+snippet, ele precisa buscar a página de origem e extrair o texto principal para produzir uma descrição comparável às outras fontes — reaproveitando a mesma heurística de extração genérica já usada na extensão de captura da Fase 2 (`job-0006`). O score de match reaproveita integralmente `CalcularAtsScore` (Fase 1, `job-0005`) e `JobDescriptionAnalyzerPort` (já existente), sem criar um segundo motor de comparação — cada vaga externa passa pelo mesmo pipeline de análise já usado no fluxo principal de adaptação.

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `VagaExterna` (novo, `domain/vaga_externa.py`): value object representando uma vaga vinda de fonte externa — `titulo`, `empresa`, `descricao`, `url`, `fonte` (enum `FonteVagaExterna`).
- `BuscadorVagasExternoPort` (novo, `application/ports/buscador_vagas_externo_port.py`): interface única implementada por cada fonte.
- `BuscadorRemoteOk`, `BuscadorWeWorkRemotely`, `BuscadorArbeitnow`, `BuscadorAdzuna`, `BuscadorGoogleCustomSearch` (novos, `infrastructure/fontes_vagas/`): um adapter HTTP por fonte, cada um convertendo a resposta específica da API para `VagaExterna`. O `BuscadorGoogleCustomSearch` difere dos demais por fazer uma segunda chamada HTTP (à página de origem do resultado) para extrair a descrição completa via `ExtratorTextoPaginaPort` (novo, reaproveita a heurística de extração genérica já definida para a extensão de captura na Fase 2).
- `DescobrirVagasComMatch` (novo use case, `application/use_cases/descobrir_vagas_com_match.py`): orquestra busca paralela nas quatro fontes, deduplicação, análise de requisitos e cálculo de match, retornando a lista ordenada.
- `JobDescriptionAnalyzerPort` (existente): reaproveitado sem alteração — cada `VagaExterna.descricao` passa por `analisar()` para virar `AnaliseVaga`, exatamente como já acontece com a vaga colada manualmente no fluxo de adaptação.
- `CalcularAtsScore` (existente, Fase 1): reaproveitado sem alteração — recebe o `Curriculo` já estruturado (extraído do currículo salvo escolhido) e a `AnaliseVaga` de cada vaga externa, retornando `ResultadoAtsScore`.
- `ExtratorCurriculoPort` (existente): reaproveitado para transformar o `CurriculoSalvo.pdf_bytes` (Fase 0) em `Curriculo` estruturado uma única vez por busca, não por vaga.

Fluxo de dados proposto:
1. UI chama `DescobrirVagasComMatch.executar(termo_busca, curriculo_salvo_id)`.
2. Use case extrai o `Curriculo` estruturado a partir do `CurriculoSalvo` (via `ExtratorCurriculoPort`, uma vez).
3. Use case dispara as cinco buscas em paralelo (`ThreadPoolExecutor`, timeout individual de 8s por fonte, exceto Google Custom Search que usa 15s por incluir a extração da página de origem); falhas/timeouts de uma fonte não interrompem as demais (resultado parcial + log de warning).
4. Resultados consolidados são deduplicados por `(titulo.lower(), empresa.lower())`.
5. Para cada `VagaExterna` restante: `JobDescriptionAnalyzerPort.analisar(descricao)` → `AnaliseVaga` → `CalcularAtsScore.executar(curriculo, analise_vaga)` → `ResultadoAtsScore`.
6. Lista final ordenada por `ResultadoAtsScore.nota` decrescente é retornada à UI.

## Design de Implementação

### Interfaces Principais

```python
class BuscadorVagasExternoPort(ABC):
    @abstractmethod
    def buscar(self, termo: str) -> tuple[VagaExterna, ...]:
        """Busca vagas pelo termo. Deve levantar TimeoutError em caso de timeout."""
        ...
```

```python
class DescobrirVagasComMatch:
    def __init__(
        self,
        buscadores: tuple[BuscadorVagasExternoPort, ...],
        analisador_vaga: JobDescriptionAnalyzerPort,
        extrator_curriculo: ExtratorCurriculoPort,
        calcular_score: CalcularAtsScore,
        repositorio_curriculo_salvo: RepositorioCurriculoSalvoPort,
    ) -> None: ...

    def executar(self, termo: str, curriculo_salvo_id: str) -> tuple[VagaComScore, ...]: ...
```

### Modelos de Dados

```python
class FonteVagaExterna(Enum):
    REMOTEOK = auto()
    WE_WORK_REMOTELY = auto()
    ARBEITNOW = auto()
    ADZUNA = auto()
    GOOGLE_CUSTOM_SEARCH = auto()

@dataclass(frozen=True)
class VagaExterna:
    titulo: str
    empresa: str
    descricao: str
    url: str
    fonte: FonteVagaExterna
    descricao_incompleta: bool = False  # True quando só há snippet (falha ao extrair a página, ex: Google Custom Search)

@dataclass(frozen=True)
class VagaComScore:
    vaga: VagaExterna
    resultado_score: ResultadoAtsScore  # reaproveitado da Fase 1
```

Não há novo esquema SQLite nesta fase — busca é sob demanda, sem persistência de resultados (ver "Fora de Escopo" no PRD: sem cache/histórico).

### Endpoints de API

Não aplicável — a busca é acionada pela UI Streamlit chamando o use case diretamente, sem passar pelo `ServidorCaptura` da Fase 2 (que é exclusivo para a extensão de navegador).

## Pontos de Integração

- RemoteOK: `GET https://remoteok.com/api?search={termo}` — API pública, sem autenticação.
- We Work Remotely: feed RSS público (`https://weworkremotely.com/categories/remote-programming-jobs.rss`) — requer parsing de XML e filtro local pelo termo, já que a fonte não oferece busca por query string.
- Arbeitnow: `GET https://www.arbeitnow.com/api/job-board-api?search={termo}` — API pública, sem autenticação.
- Adzuna: `GET https://api.adzuna.com/v1/api/jobs/{pais}/search/1?app_id={id}&app_key={key}&what={termo}` — requer `app_id`/`app_key` gratuitos (cadastro simples); credenciais via variáveis de ambiente (`ADZUNA_APP_ID`, `ADZUNA_APP_KEY`), seguindo o padrão já usado para `GROQ_API_KEY` no `.env`.
- Google Custom Search: `GET https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={termo}` — API oficial, requer `api_key` (Google Cloud) e `cx` (id de um Programmable Search Engine configurado previamente no console do Google); credenciais via `GOOGLE_CSE_API_KEY` e `GOOGLE_CSE_ID` no `.env`. Cota gratuita de 100 buscas/dia; ao esgotar, a API retorna HTTP 429 — o adapter deve tratar esse status especificamente e retornar tupla vazia com log de warning, sem propagar erro.
- `ExtratorTextoPaginaPort` (novo, `application/ports/extrator_texto_pagina_port.py`): usado apenas pelo `BuscadorGoogleCustomSearch` para buscar a página de cada resultado (`GET` simples) e extrair o texto principal via heurística genérica — mesma abordagem de `content.js` da extensão (Fase 2), mas em Python (`httpx` + `BeautifulSoup` ou similar) do lado do servidor. Se a extração falhar ou a página bloquear o acesso, retorna o snippet original e marca `descricao_incompleta=True`.
- Tratamento de erro: cada adapter deve capturar exceções de rede/timeout e traduzi-las para `TimeoutError` ou retornar tupla vazia, nunca propagar exceção não tratada para o use case orquestrador.

## Abordagem de Testes

### Testes Unidade

- `DescobrirVagasComMatch`: usando fakes de `BuscadorVagasExternoPort` (um por fonte), validando deduplicação, ordenação por score, e resiliência quando uma fonte falha/expira.
- Cada adapter (`BuscadorRemoteOk`, etc.): teste unitário com resposta HTTP mockada (fixture JSON/XML real de exemplo), validando o mapeamento correto para `VagaExterna`.
- `BuscadorGoogleCustomSearch`: teste unitário cobrindo (a) extração bem-sucedida da página de origem, (b) fallback para snippet quando a extração falha, e (c) tratamento do HTTP 429 de cota esgotada retornando tupla vazia sem exceção.
- Reaproveitamento: nenhum teste novo é necessário para `CalcularAtsScore` ou `JobDescriptionAnalyzerPort` — já cobertos nas fases anteriores.

### Testes de Serviço

- Teste de integração do fluxo completo com todos os quatro adapters mockados via `responses`/`httpx` mock, validando que uma falha isolada (ex: Adzuna retornando 500) não impede a exibição das demais vagas.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. `VagaExterna`, `FonteVagaExterna`, `VagaComScore` (domain) — sem dependências.
2. `BuscadorVagasExternoPort` + os quatro adapters de API direta (RemoteOK, WWR, Arbeitnow, Adzuna), cada um testado isoladamente com fixtures mockadas.
3. `ExtratorTextoPaginaPort` + `BuscadorGoogleCustomSearch`, incluindo o caminho de fallback para snippet — feito depois dos demais por ter uma etapa a mais (busca da página de origem).
4. `DescobrirVagasComMatch`, reaproveitando `CalcularAtsScore` e `JobDescriptionAnalyzerPort` já existentes — com testes usando fakes dos buscadores.
5. Integração na UI: tela de busca por termo + seleção de currículo salvo + lista de resultados ordenada com detalhe de requisitos batidos/faltantes (reaproveitando o componente visual já criado na Fase 1 para o ATS Score), incluindo indicação visual quando `descricao_incompleta=True`.
6. Botão "criar candidatura a partir desta vaga", integrando com o Kanban da Fase 2.
7. Validação manual com termos de busca reais contra as cinco fontes.

### Dependências Técnicas

- Nova dependência: `httpx` (cliente HTTP com suporte a timeout simples), `feedparser` (parsing do RSS da We Work Remotely) e `beautifulsoup4` (extração de texto da página nos resultados do Google) — adicionar a `requirements.txt`.
- Credenciais gratuitas da Adzuna (`app_id`/`app_key`) precisam ser obtidas pelo usuário antes desta fase funcionar completamente; as outras três fontes de API direta não exigem cadastro.
- Google Custom Search exige duas configurações prévias no console do Google: uma API key (Google Cloud) e um Programmable Search Engine (`cx`) — ambos gratuitos, mas exigem cadastro manual antes desta fonte funcionar.
- Depende da Fase 0 (biblioteca de currículos salvos) e da Fase 1 (`CalcularAtsScore`) já implementadas.

## Monitoramento e Observabilidade

- Logar (WARNING) timeout ou erro de cada fonte individualmente, incluindo qual fonte falhou, sem interromper o fluxo.
- Logar (INFO) quantidade de vagas retornadas por fonte e quantidade final após deduplicação, por busca realizada.

## Considerações Técnicas

### Decisões Principais

- Busca sob demanda, sem cache/histórico: mantém a implementação simples nesta fase; um mecanismo de alerta recorrente (mencionado como questão em aberto no PRD) exigiria um scheduler e fica deliberadamente fora do escopo até ser confirmado como necessário.
- Reaproveitamento total do motor de análise/score das fases anteriores: evita duplicar a lógica de comparação de requisitos, garantindo que o critério de match seja consistente entre "ATS Score de uma adaptação manual" e "score de uma vaga descoberta".
- Paralelismo com `ThreadPoolExecutor` (não `asyncio`): consistente com o restante do projeto, que não usa código assíncrono em nenhum outro ponto; evita introduzir dois paradigmas de concorrência diferentes.

### Riscos Conhecidos

- APIs públicas gratuitas podem mudar formato de resposta ou impor rate limit sem aviso — mitigação: cada adapter isolado, falha em uma fonte não derruba as demais.
- We Work Remotely via RSS não suporta busca por termo nativamente, exigindo filtro local no texto do feed — pode gerar resultados menos precisos que as demais fontes com busca real.
- Analisar cada vaga externa via `JobDescriptionAnalyzerPort` (que usa a API Groq) para uma lista grande de resultados pode gerar custo/latência perceptível — mitigação: limitar a quantidade de vagas analisadas por busca (ex: top 20 por fonte antes da análise), a validar como questão em aberto de produto.
- Cota gratuita do Google Custom Search (100 buscas/dia) é compartilhada por todos os perfis do sistema (mesma chave) — em uso intenso, pode esgotar rapidamente; mitigação já prevista de degradar graciosamente para as demais fontes.
- A extração de texto da página de origem (para resultados do Google) depende do site de destino permitir acesso simples (sem JavaScript obrigatório, sem bloqueio a bots) — sites que exigem renderização client-side vão cair no fallback de snippet, resultando em descrição incompleta com mais frequência que as demais fontes.

### Conformidade com Padrões

Não há regras em `.windsurf/rules` no repositório (diretório inexistente) — nenhum desvio a documentar. Mantém a Arquitetura Hexagonal: os quatro clientes HTTP são adapters de infraestrutura implementando uma porta comum, sem lógica de negócio além da tradução de formato.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/analise-de-vagas/job-0007-descoberta-e-match-de-vagas/prd-job-0007.md`
- `domain/vaga_externa.py` (novo)
- `application/ports/buscador_vagas_externo_port.py` (novo)
- `application/ports/extrator_texto_pagina_port.py` (novo)
- `application/use_cases/descobrir_vagas_com_match.py` (novo)
- `infrastructure/fontes_vagas/buscador_remoteok.py`, `buscador_wwr.py`, `buscador_arbeitnow.py`, `buscador_adzuna.py`, `buscador_google_custom_search.py` (novos)
- `infrastructure/fontes_vagas/extrator_texto_pagina.py` (novo)
- `application/use_cases/calcular_ats_score.py` (existente, Fase 1 — reaproveitado sem alteração)
- `application/ports/job_description_analyzer_port.py` (existente — reaproveitado sem alteração)
- `application/ports/extrator_curriculo_port.py` (existente — reaproveitado sem alteração)
- `ui/app_streamlit.py` (modificado)
- `requirements.txt` (modificado — `httpx`, `feedparser`, `beautifulsoup4`)

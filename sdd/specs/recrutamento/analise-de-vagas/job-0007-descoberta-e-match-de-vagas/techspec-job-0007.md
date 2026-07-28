# Especificação Técnica

## Resumo Executivo

Esta Tech Spec descreve a implementação da busca de vagas em fontes externas, do cálculo de match e da candidatura em um clique, conforme `prd-job-0007.md`. A abordagem introduz uma porta única `BuscadorVagasExternoPort` com cinco adapters (RemoteOK, We Work Remotely, Arbeitnow, Adzuna, Google Custom Search), consultados em paralelo com timeout individual. O adapter do Google Custom Search tem uma responsabilidade extra em relação aos demais: como a API só devolve link+snippet, ele precisa buscar a página de origem e extrair o texto principal para produzir uma descrição comparável às outras fontes — reaproveitando a mesma heurística de extração genérica já usada na extensão de captura da Fase 2 (`job-0006`). O score de match reaproveita integralmente `CalcularAtsScore` (Fase 1, `job-0005`) e `JobDescriptionAnalyzerPort` (já existente), sem criar um segundo motor de comparação — cada vaga externa passa pelo mesmo pipeline de análise já usado no fluxo principal de adaptação. Um segundo use case, `CandidatarNaVagaExterna`, implementa o botão "Candidatar": roda a extração do currículo, análise da vaga, adaptação de todas as seções (mesma lógica de `AdaptarCurriculoParaVaga`), cálculo de ATS Score e geração de carta de apresentação — sem chamar os outros use cases diretamente (regra do projeto: um caso de uso nunca chama outro), reaproveitando apenas as portas e o Domain Service `CalcularAtsScore`, no mesmo padrão já usado por `AnalisarAtsVaga` (Fase 1).

Nota sobre caminhos: esta Tech Spec foi escrita antes da migração do projeto para a estrutura `src/domain`/`src/application`/`src/infrastructure`/`src/ui` (Ports and Adapters com portas co-localizadas em `domain.<agregado>`, use cases como pacotes `dtos.py`/`use_case.py`/`validator.py`/`__init__.py`). Todos os caminhos abaixo já refletem essa convenção.

Adendo (filtro por período): `VagaExterna` ganha um campo `data_publicacao: date | None`, populado por cada adapter a partir do campo de data específico da fonte (quando existir). `DescobrirVagasComMatch.executar` passa a aceitar um parâmetro opcional `dias_maximo` (7/15/30/`None`). Para a Adzuna, que tem suporte nativo (`max_days_old`), o filtro é aplicado na própria chamada HTTP; para as demais fontes, o filtro é aplicado depois de buscar, comparando `data_publicacao` com a data atual. Vagas sem data determinável (tipicamente Google Custom Search) continuam aparecendo mesmo com o filtro ativo — decisão de produto documentada no PRD.

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `VagaExterna` (novo, `src/domain/vaga_externa/__init__.py`): value object representando uma vaga vinda de fonte externa — `titulo`, `empresa`, `descricao`, `url`, `fonte` (enum `FonteVagaExterna`), `descricao_incompleta`.
- `BuscadorVagasExternoPort` (novo, `src/domain/vaga_externa/buscador_vagas_externo_port.py`): interface única implementada por cada fonte, co-localizada no agregado `vaga_externa` (convenção do projeto: portas vivem em `domain.<agregado>`).
- `ExtratorTextoPaginaPort` (novo, `src/domain/vaga_externa/extrator_texto_pagina_port.py`).
- `BuscadorRemoteOk`, `BuscadorWeWorkRemotely`, `BuscadorArbeitnow`, `BuscadorAdzuna`, `BuscadorGoogleCustomSearch` (novos, `src/infrastructure/fontes_vagas/`): um adapter HTTP por fonte, cada um convertendo a resposta específica da API para `VagaExterna`. O `BuscadorGoogleCustomSearch` difere dos demais por fazer uma segunda chamada HTTP (à página de origem do resultado) para extrair a descrição completa via `ExtratorTextoPaginaPort`.
- `DescobrirVagasComMatch` (novo use case, `src/application/use_cases/descobrir_vagas_com_match/`): orquestra busca paralela nas cinco fontes, deduplicação, análise de requisitos e cálculo de match, retornando a lista ordenada.
- `CandidatarNaVagaExterna` (novo use case, `src/application/use_cases/candidatar_na_vaga_externa/`): implementa o botão "Candidatar" — extrai o currículo, analisa a vaga, adapta todas as seções, calcula o ATS Score e gera a carta de apresentação para a vaga escolhida. Depende diretamente das portas (`ExtratorCurriculoPort`, `JobDescriptionAnalyzerPort`, `AjustadorTextoPort`, `GeradorPdfPort`, `GerarCartaApresentacaoPort`) e do Domain Service `CalcularAtsScore` — não chama `AdaptarCurriculoParaVaga` nem `GerarCartaApresentacao` (regra do projeto: use case nunca chama outro use case), reaproveitando a mesma abordagem já usada por `AnalisarAtsVaga` (Fase 1).
- `JobDescriptionAnalyzerPort` (existente): reaproveitado sem alteração — cada `VagaExterna.descricao` passa por `analisar()` para virar `AnaliseVaga`, exatamente como já acontece com a vaga colada manualmente no fluxo de adaptação.
- `CalcularAtsScore` (existente, Fase 1, Domain Service em `src/domain/ats_score/calcular_ats_score_service.py`): reaproveitado sem alteração — recebe o `Curriculo` já estruturado e a `AnaliseVaga` de cada vaga externa, retornando `ResultadoAtsScore`.
- `ExtratorCurriculoPort`, `AjustadorTextoPort`, `GeradorPdfPort`, `GerarCartaApresentacaoPort` (existentes, em `src/domain/curriculo/`): reaproveitados sem alteração.

Fluxo de dados proposto:
1. UI chama `DescobrirVagasComMatch.executar(termo_busca, pdf_curriculo)`, com os bytes do `CurriculoSalvo` já escolhido (via `ListarCurriculosSalvos`, Fase 0).
2. Use case extrai o `Curriculo` estruturado a partir do `pdf_curriculo` (via `ExtratorCurriculoPort`, uma vez).
3. Use case dispara as cinco buscas em paralelo (`ThreadPoolExecutor`, timeout individual de 8s por fonte, exceto Google Custom Search que usa 15s por incluir a extração da página de origem), repassando `dias_maximo` a cada buscador (só a Adzuna usa esse valor na chamada HTTP; as demais o ignoram); falhas/timeouts de uma fonte não interrompem as demais (resultado parcial + log de warning).
4. Resultados consolidados são deduplicados por `(titulo.lower(), empresa.lower())`.
4.1. Se `dias_maximo` foi informado, filtra a lista deduplicada mantendo apenas vagas com `data_publicacao is None` (data desconhecida, sempre mantida) ou `data_publicacao` dentro da janela solicitada.
5. Trunca a lista para no máximo `LIMITE_VAGAS_ANALISADAS` (mitigação de custo/cota, ver "Riscos Conhecidos"). Para cada `VagaExterna` restante: `JobDescriptionAnalyzerPort.analisar(descricao)` → `AnaliseVaga` → `CalcularAtsScore.executar(curriculo, analise_vaga)` → `ResultadoAtsScore`.
6. Lista final ordenada por `ResultadoAtsScore.nota` decrescente é retornada à UI.

Fluxo de dados do "Candidatar" (`CandidatarNaVagaExterna`):
1. UI chama `CandidatarNaVagaExterna.executar(input_dto)` com o PDF do currículo salvo escolhido, os dados da `VagaExterna` (título, empresa, descrição, url) e o idioma alvo.
2. Use case extrai o `Curriculo` (`ExtratorCurriculoPort`), analisa a vaga (`JobDescriptionAnalyzerPort`) e ajusta cada seção do currículo (`AjustadorTextoPort`), replicando a mesma lógica de `AdaptarCurriculoParaVaga.executar`.
3. Gera o PDF adaptado (`GeradorPdfPort`) e o nome de arquivo padronizado (`NomeArquivo`).
4. Calcula o ATS Score do currículo adaptado contra a vaga (`CalcularAtsScore`, Domain Service).
5. Gera a carta de apresentação (`GerarCartaApresentacaoPort`) usando o currículo adaptado e a análise da vaga.
6. Retorna `pdf_bytes`, `nome_arquivo`, `resultado_ats`, `carta_apresentacao` e a `url_vaga` original (repassada do input, sem alteração) — a UI usa essa URL para abrir a vaga em nova aba (`st.link_button`) e oferece os demais artefatos para download.

## Design de Implementação

### Interfaces Principais

```python
class BuscadorVagasExternoPort(ABC):
    @abstractmethod
    def buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]:
        """Busca vagas pelo termo, opcionalmente restrito a publicações recentes.

        `dias_maximo` é um hint best-effort: só a Adzuna o usa nativamente na
        chamada HTTP (`max_days_old`); as demais fontes o ignoram e retornam
        o campo `data_publicacao` (quando disponível) para filtro posterior
        pelo use case orquestrador. Deve levantar TimeoutError em caso de timeout.
        """
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
    ) -> None: ...

    def executar(
        self, termo: str, pdf_curriculo: bytes, dias_maximo: int | None = None
    ) -> tuple[VagaComScore, ...]: ...
```

Nota: recebe `pdf_curriculo: bytes` diretamente (não um id + repositório), mesmo padrão já usado em `AnalisarAtsVaga` e `AdaptarCurriculoParaVaga` — a UI já tem os bytes do `CurriculoSalvo` selecionado (via `ListarCurriculosSalvos`, Fase 0) antes de chamar o use case, então não há necessidade de uma dependência de repositório aqui.

```python
class CandidatarNaVagaExterna:
    def __init__(
        self,
        extrator: ExtratorCurriculoPort,
        analisador_vaga: JobDescriptionAnalyzerPort,
        ajustador_texto: AjustadorTextoPort,
        gerador_pdf: GeradorPdfPort,
        calcular_ats_score: CalcularAtsScore,
        gerador_carta: GerarCartaApresentacaoPort,
    ) -> None: ...

    def executar(self, input_dto: CandidatarNaVagaExternaInputDto) -> CandidatarNaVagaExternaOutputDto: ...
```

```python
@dataclass(frozen=True)
class CandidatarNaVagaExternaInputDto:
    pdf_curriculo: bytes
    vaga: VagaExterna
    idioma_alvo: str
    cargo_alvo: str
    empresa_alvo: str
    data_referencia: date | None = None

@dataclass(frozen=True)
class CandidatarNaVagaExternaOutputDto:
    pdf_bytes: bytes
    nome_arquivo: NomeArquivo
    resultado_ats: ResultadoAtsScore
    carta_apresentacao: str
    url_vaga: str
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
    data_publicacao: date | None = None  # None quando a fonte não informa data confiável (ex: Google Custom Search)

@dataclass(frozen=True)
class VagaComScore:
    vaga: VagaExterna
    resultado_score: ResultadoAtsScore  # reaproveitado da Fase 1
```

Não há novo esquema SQLite nesta fase — busca é sob demanda, sem persistência de resultados (ver "Fora de Escopo" no PRD: sem cache/histórico).

### Endpoints de API

Não aplicável — a busca é acionada pela UI Streamlit chamando o use case diretamente, sem passar pelo `ServidorCaptura` da Fase 2 (que é exclusivo para a extensão de navegador).

## Pontos de Integração

- RemoteOK: `GET https://remoteok.com/api?search={termo}` — API pública, sem autenticação. Campo de data: `date` (string ISO 8601) — parseado via `datetime.fromisoformat` para preencher `data_publicacao`; sem parâmetro nativo de filtro por data.
- We Work Remotely: feed RSS público (`https://weworkremotely.com/categories/remote-programming-jobs.rss`) — requer parsing de XML e filtro local pelo termo, já que a fonte não oferece busca por query string. Campo de data: `published_parsed` (fornecido pelo `feedparser` como `time.struct_time`) — convertido para `date`; sem parâmetro nativo de filtro por data.
- Arbeitnow: `GET https://www.arbeitnow.com/api/job-board-api?search={termo}` — API pública, sem autenticação. Campo de data: `created_at` (timestamp Unix) — convertido via `datetime.fromtimestamp`; sem parâmetro nativo de filtro por data.
- Adzuna: `GET https://api.adzuna.com/v1/api/jobs/{pais}/search/1?app_id={id}&app_key={key}&what={termo}` — requer `app_id`/`app_key` gratuitos (cadastro simples); credenciais via variáveis de ambiente (`ADZUNA_APP_ID`, `ADZUNA_APP_KEY`), seguindo o padrão já usado para `GROQ_API_KEY` no `.env`. Campo de data: `created` (string ISO 8601). **Suporte nativo a filtro por período**: quando `dias_maximo` é informado, o adapter adiciona `max_days_old={dias_maximo}` à query string, filtrando no próprio servidor da Adzuna (mais eficiente que filtrar depois de baixar os resultados).
- Google Custom Search: `GET https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={termo}` — API oficial, requer `api_key` (Google Cloud) e `cx` (id de um Programmable Search Engine configurado previamente no console do Google); credenciais via `GOOGLE_CSE_API_KEY` e `GOOGLE_CSE_ID` no `.env`. Cota gratuita de 100 buscas/dia; ao esgotar, a API retorna HTTP 429 — o adapter deve tratar esse status especificamente e retornar tupla vazia com log de warning, sem propagar erro. Não há campo de data de publicação da vaga em si — `data_publicacao` fica sempre `None` para esta fonte (a API não devolve quando a vaga foi publicada, só quando o Google indexou a página, que são coisas diferentes); não usar o parâmetro `dateRestrict` do Google para tentar aproximar isso, pois filtraria por data de indexação e daria uma falsa sensação de precisão ao usuário.
- `ExtratorTextoPaginaPort` (novo, `src/domain/vaga_externa/extrator_texto_pagina_port.py`): usado apenas pelo `BuscadorGoogleCustomSearch` para buscar a página de cada resultado (`GET` simples) e extrair o texto principal via heurística genérica — mesma abordagem de `content.js` da extensão (Fase 2), mas em Python (`httpx` + `BeautifulSoup` ou similar) do lado do servidor. Se a extração falhar ou a página bloquear o acesso, retorna o snippet original e marca `descricao_incompleta=True`.
- Tratamento de erro: cada adapter deve capturar exceções de rede/timeout e traduzi-las para `TimeoutError` ou retornar tupla vazia, nunca propagar exceção não tratada para o use case orquestrador.

## Abordagem de Testes

### Testes Unidade

- `DescobrirVagasComMatch`: usando fakes de `BuscadorVagasExternoPort` (um por fonte), validando deduplicação, ordenação por score, resiliência quando uma fonte falha/expira, o corte por `LIMITE_VAGAS_ANALISADAS`, e o filtro por `dias_maximo` (vaga dentro da janela, vaga fora da janela, vaga com `data_publicacao=None` sempre mantida).
- Cada adapter (`BuscadorRemoteOk`, etc.): teste unitário com resposta HTTP mockada (fixture JSON/XML real de exemplo), validando o mapeamento correto para `VagaExterna`, incluindo o parsing do campo de data específico da fonte para `data_publicacao`.
- `BuscadorAdzuna`: teste adicional confirmando que `dias_maximo` é repassado como `max_days_old` na query string quando informado, e omitido quando `None`.
- `BuscadorGoogleCustomSearch`: teste unitário cobrindo (a) extração bem-sucedida da página de origem, (b) fallback para snippet quando a extração falha, e (c) tratamento do HTTP 429 de cota esgotada retornando tupla vazia sem exceção.
- Reaproveitamento: nenhum teste novo é necessário para `CalcularAtsScore` ou `JobDescriptionAnalyzerPort` — já cobertos nas fases anteriores.
- `CandidatarNaVagaExterna`: usando fakes de `ExtratorCurriculoPort`, `JobDescriptionAnalyzerPort`, `AjustadorTextoPort`, `GeradorPdfPort` e `GerarCartaApresentacaoPort` (mesmos fakes já usados nos testes de `AdaptarCurriculoParaVaga` e `GerarCartaApresentacao`), validando que o output contém PDF adaptado, `ResultadoAtsScore`, carta de apresentação e a `url_vaga` repassada sem alteração.

### Testes de Serviço

- Teste de integração do fluxo completo com todos os cinco adapters mockados via `responses`/`httpx` mock, validando que uma falha isolada (ex: Adzuna retornando 500) não impede a exibição das demais vagas.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. `VagaExterna`, `FonteVagaExterna`, `VagaComScore` (domain) — sem dependências.
2. `BuscadorVagasExternoPort` + os quatro adapters de API direta (RemoteOK, WWR, Arbeitnow, Adzuna), cada um testado isoladamente com fixtures mockadas.
3. `ExtratorTextoPaginaPort` + `BuscadorGoogleCustomSearch`, incluindo o caminho de fallback para snippet — feito depois dos demais por ter uma etapa a mais (busca da página de origem).
4. `DescobrirVagasComMatch`, reaproveitando `CalcularAtsScore` e `JobDescriptionAnalyzerPort` já existentes — com testes usando fakes dos buscadores.
5. `CandidatarNaVagaExterna`, reaproveitando as portas de currículo/vaga/carta já existentes (mesmo padrão de `AnalisarAtsVaga`) — com testes usando os fakes já existentes dessas portas.
6. Integração na UI: item de menu lateral "Vagas" com tela de busca por termo + seleção de currículo salvo + lista de resultados ordenada com detalhe de requisitos batidos/faltantes (reaproveitando o componente visual já criado na Fase 1 para o ATS Score), incluindo indicação visual quando `descricao_incompleta=True`.
7. Botão "Candidatar" em cada vaga da lista: roda `CandidatarNaVagaExterna`, exibe o PDF adaptado e a carta de apresentação para download, e abre a URL original da vaga em nova aba (`st.link_button`).
8. Validação manual com termos de busca reais contra as cinco fontes e do fluxo de candidatura completo.
9. Filtro por período: adicionar `data_publicacao` a `VagaExterna`, parsing por adapter, parâmetro `dias_maximo` em `BuscadorVagasExternoPort.buscar` e em `DescobrirVagasComMatch.executar` (uso nativo na Adzuna, filtro local nas demais), seletor de período na UI "Vagas" e exibição da data (ou "desconhecida") em cada vaga da lista.

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
- Analisar cada vaga externa via `JobDescriptionAnalyzerPort` (que usa a API Groq) para uma lista grande de resultados pode gerar custo/latência perceptível — **confirmado em teste manual real**: uma busca com termo genérico retornou 200+ vagas únicas e esgotou a cota diária inteira da conta Groq (200k tokens) em uma única chamada. Mitigação implementada: `LIMITE_VAGAS_ANALISADAS = 20` em `DescobrirVagasComMatch` corta a lista deduplicada antes da etapa de análise/score.
- Cota gratuita do Google Custom Search (100 buscas/dia) é compartilhada por todos os perfis do sistema (mesma chave) — em uso intenso, pode esgotar rapidamente; mitigação já prevista de degradar graciosamente para as demais fontes.
- A extração de texto da página de origem (para resultados do Google) depende do site de destino permitir acesso simples (sem JavaScript obrigatório, sem bloqueio a bots) — sites que exigem renderização client-side vão cair no fallback de snippet, resultando em descrição incompleta com mais frequência que as demais fontes.
- O filtro por período não é uniformemente confiável entre fontes: Adzuna filtra no servidor (confiável), RemoteOK/WWR/Arbeitnow dependem do parsing correto do campo de data de cada API (pode falhar silenciosamente se o formato mudar, resultando em `data_publicacao=None` e a vaga sendo mantida mesmo fora da janela pedida), e Google Custom Search nunca tem data confiável. Usuário deve entender que o filtro é "melhor esforço", não uma garantia absoluta para todas as fontes.

### Conformidade com Padrões

Segue `.windsurf/rules/code-design-standards.md`: portas co-localizadas em `domain.<agregado>` (`vaga_externa`), use cases como pacotes (`dtos.py`/`use_case.py`/`validator.py`/`__init__.py`), `CandidatarNaVagaExterna` nunca chama outro use case (reaproveita apenas portas e o Domain Service `CalcularAtsScore`, mesmo padrão de `AnalisarAtsVaga`). Mantém a Arquitetura Hexagonal: os cinco clientes HTTP são adapters de infraestrutura implementando uma porta comum, sem lógica de negócio além da tradução de formato.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/analise-de-vagas/job-0007-descoberta-e-match-de-vagas/prd-job-0007.md`
- `src/domain/vaga_externa/__init__.py` (novo — `VagaExterna`, `FonteVagaExterna`, `VagaComScore`)
- `src/domain/vaga_externa/buscador_vagas_externo_port.py` (novo)
- `src/domain/vaga_externa/extrator_texto_pagina_port.py` (novo)
- `src/application/use_cases/descobrir_vagas_com_match/{dtos,use_case,validator,__init__}.py` (novo)
- `src/application/use_cases/candidatar_na_vaga_externa/{dtos,use_case,validator,__init__}.py` (novo)
- `src/infrastructure/fontes_vagas/buscador_remoteok.py`, `buscador_wwr.py`, `buscador_arbeitnow.py`, `buscador_adzuna.py`, `buscador_google_custom_search.py` (novos)
- `src/infrastructure/fontes_vagas/extrator_texto_pagina.py` (novo)
- `src/domain/ats_score/calcular_ats_score_service.py` (existente, Fase 1 — reaproveitado sem alteração)
- `src/domain/vaga/job_description_analyzer_port.py` (existente — reaproveitado sem alteração)
- `src/domain/curriculo/extrator_curriculo_port.py`, `ajustador_texto_port.py`, `gerador_pdf_port.py`, `gerar_carta_apresentacao_port.py` (existentes — reaproveitados sem alteração)
- `src/ui/app_streamlit.py` (modificado — novo item de menu "Vagas" com seletor de período; usa `ListarCurriculosSalvos`, Fase 0, já existente, para a seleção do currículo)
- `requirements.txt` (modificado — `httpx`, `feedparser`, `beautifulsoup4`)
- `src/tests/domain/vaga_externa/`, `src/tests/application/use_cases/descobrir_vagas_com_match/`, `src/tests/application/use_cases/candidatar_na_vaga_externa/`, `src/tests/infrastructure/fontes_vagas/` (novos)

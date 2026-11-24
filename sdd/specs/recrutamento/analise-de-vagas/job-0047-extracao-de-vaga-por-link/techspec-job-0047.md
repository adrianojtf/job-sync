# Especificação Técnica

Referência: [PRD job-0047](prd-job-0047.md)

## Resumo Executivo

Um novo caso de uso `ExtrairDadosVaga`, no domínio `vaga`, recebe um link e/ou um texto e devolve um rascunho `DadosVaga` (cargo, empresa, local, descrição e campos secundários), sem persistir nada. Ele é exposto em `POST /v1/vagas/extracoes` e consumido por "Ajustar currículo para vaga" e pela captura de vagas.

O caso de uso depende de duas portas novas no domínio: `LeitorVagaPorLinkPort` (link para dados) e `ExtratorDadosVagaDeTextoPort` (texto para dados). O leitor do LinkedIn usa a versão pública da vaga (endpoint de visitante) e interpreta o HTML de forma determinística. Outros sites usam JSON-LD `JobPosting`, com a LLM como alternativa. Texto colado vai direto à LLM. Toda busca HTTP passa por um cliente com proteção contra SSRF em `shared_kernel`. A captura passa a guardar `cargo`, `empresa` e `local` em colunas opcionais, de forma aditiva.

## Arquitetura do Sistema

### Visão Geral dos Componentes

**Novos, domínio `vaga/domain`:**
- `dados_vaga.py`: `DadosVaga`, objeto de valor imutável com validação.
- `link_vaga.py`: `LinkVaga`, objeto de valor que valida, normaliza o link, identifica a fonte (`FonteVaga.LINKEDIN` ou `OUTRA`) e o id da vaga do LinkedIn.
- `leitor_vaga_por_link_port.py`: porta `LeitorVagaPorLinkPort`.
- `extrator_dados_vaga_de_texto_port.py`: porta `ExtratorDadosVagaDeTextoPort`.
- `limitador_leitura_vaga_port.py`: porta `LimitadorLeituraVagaPort`.
- `exceptions.py`: `LinkVagaInvalido`, `FonteVagaNaoSuportada`, `LeituraVagaIndisponivel`, `LimiteLeituraVagaExcedido`.

**Novos, `vaga/service_layer/extrair_dados_vaga/`:** `dtos.py`, `validator.py`, `service.py` (`ExtrairDadosVaga`).

**Novos, `vaga/adapters`:**
- `leitor_vaga_linkedin_client.py`: monta a URL de visitante a partir do id e interpreta o HTML com BeautifulSoup.
- `leitor_vaga_generico_client.py`: busca a página, lê o JSON-LD `JobPosting` e, na falta dele, delega o texto da página ao extrator por IA.
- `extrator_dados_vaga_ia_client.py`: usa `ClienteOpenAI.solicitar_json`.
- `limitador_leitura_vaga_em_memoria.py`: janela deslizante por usuário.

**Novo, `shared_kernel/adapters/cliente_http_seguro.py`:** cliente HTTP com proteção contra SSRF.

**Alterados:**
- `vaga/domain/vaga.py`: campos opcionais `cargo`, `empresa`, `local`.
- `vaga/adapters/vaga_repository_impl.py` e `vaga_repository_fake.py`: gravam e leem os novos campos.
- `vaga/service_layer/capturar_vaga/dtos.py` e `validator.py`: aceitam os novos campos.
- `shared_kernel/adapters/persistence/migracoes/0005_vaga_dados_extraidos.sql`: colunas `cargo`, `empresa`, `local`, todas nulas.
- `entrypoints/api/routers/vaga_router.py`, `schemas/vaga.py`, `dependencies.py` (injeção do serviço) e `exceptions.py` (handlers).
- `frontend`: campo "Link da vaga" em `AjustarVagaPage.tsx` e `vagas-salvas/ColarVagaModal.tsx`, novo componente `CampoLinkVaga`, hook `use-extrair-dados-vaga.ts`, `api-client.ts`, `http-api-client.ts` e `schema.d.ts` regenerado.
- `.env.example`: variáveis novas.

**Fluxo de dados:**
1. O front envia `url` e/ou `texto` para `POST /v1/vagas/extracoes`.
2. O serviço aplica o limite por usuário.
3. Se houver texto, usa o extrator por IA e encerra. O texto tem prioridade.
4. Se houver só a URL, cria o `LinkVaga` (normaliza e identifica a fonte) e escolhe o leitor pela fonte.
5. O leitor devolve `DadosVaga` ou levanta `LeituraVagaIndisponivel`.
6. A API devolve o rascunho. O front preenche os campos para revisão. Em falha, mostra o motivo e oferece colar o texto.

## Design de Implementação

### Interfaces Principais

```python
class LeitorVagaPorLinkPort(ABC):
    @abstractmethod
    def ler(self, link: LinkVaga) -> DadosVaga: ...

class ExtratorDadosVagaDeTextoPort(ABC):
    @abstractmethod
    def extrair(self, texto: str) -> DadosVaga: ...

class LimitadorLeituraVagaPort(ABC):
    @abstractmethod
    def registrar(self, usuario_id: str) -> None: ...

class ExtrairDadosVaga:
    def __init__(self, leitores: Mapping[FonteVaga, LeitorVagaPorLinkPort],
                 extrator_texto: ExtratorDadosVagaDeTextoPort,
                 limitador: LimitadorLeituraVagaPort,
                 linkedin_habilitado: bool) -> None: ...
    def executar(self, entrada: ExtrairDadosVagaInputDto) -> DadosVaga: ...
```

O `ExtrairDadosVaga` é o único ponto que decide fonte, prioridade e chave de desligamento. Os adapters não conhecem uns aos outros.

### Modelos de Dados

- `DadosVaga` (imutável): `cargo`, `empresa`, `local`, `descricao` (obrigatória, texto original), `url` (normalizada, opcional), `tipo_contratacao`, `senioridade`, `setor` (opcionais). Campos de texto são aparados e limitados em tamanho.
- `LinkVaga`: aceita só `http` e `https`; remove parâmetros de rastreamento (`trk`, `utm_*`, `refId`, `trackingId` e similares) e fragmentos. Para o LinkedIn, extrai o id de `/jobs/view/{slug}-{id}` e `/jobs/view/{id}` e do parâmetro `currentJobId` em links de busca. Sem id válido, levanta `LinkVagaInvalido`.
- Tabela `vaga`: colunas `cargo TEXT NULL`, `empresa TEXT NULL`, `local TEXT NULL`. Linhas antigas ficam com nulos.

### Endpoints de API

`POST /v1/vagas/extracoes`
- Corpo: `{ "url": string?, "texto": string? }`, com pelo menos um dos dois.
- 200: `{ cargo, empresa, local, descricao, url, tipo_contratacao, senioridade, setor }` (campos ausentes vêm nulos).
- 422: link inválido, nenhum dado informado, ou fonte não suportada (LinkedIn desligado).
- 429: limite de uso, com cabeçalho `Retry-After`.
- 502: leitura indisponível (bloqueio, vaga encerrada, página sem dados, tempo esgotado). O `detail` explica o motivo em linguagem simples.
- Erros no formato RFC 7807, por handlers centrais em `exceptions.py`. A rota fica sob `exigir_perfil_da_requisicao`. O limite usa o usuário autenticado.

Contratos alterados, apenas de forma aditiva: `VagaCapturarRequest` e `VagaResponse` ganham `cargo`, `empresa`, `local` opcionais (PRD, RF 23).

## Pontos de Integração

- **LinkedIn (versão pública, sem login):** endpoint de visitante, não documentado e sem contrato. Uma única requisição por link, sem repetição após 429 ou desafio. O leitor interpreta o HTML pelas classes da seção da vaga (título, empresa, local, descrição, critérios). Se faltar título ou descrição, levanta `LeituraVagaIndisponivel`.
- **Outros sites:** HTTP simples pelo cliente seguro. JSON-LD `JobPosting` primeiro. Na falta dele, texto da página para a LLM.
- **OpenAI (`ClienteOpenAI`):** extração a partir de texto. O prompt trata o texto como dado, nunca como instrução, devolve só os campos pedidos em JSON e não inventa valores. O texto é truncado em 20.000 caracteres. A saída é validada em tipo e tamanho antes de virar `DadosVaga`.
- **Cliente HTTP seguro:** para cada requisição e cada redirecionamento, resolve o DNS e recusa IPs de loopback, redes privadas, link-local e metadados de nuvem. Conecta no IP validado, com o nome original para SNI (extensão `sni_hostname` do `httpx`) e cabeçalho `Host`. Limita redirecionamentos (5), tamanho (2 MB) e tempo (15 s). Aceita só `http` e `https`.

Configuração por variáveis de ambiente (leitura na composição, em `dependencies.py`): `VAGA_LEITURA_LINKEDIN_HABILITADA` (padrão `true`), `VAGA_LEITURA_LIMITE_POR_MINUTO` (10), `VAGA_LEITURA_LIMITE_POR_DIA` (100), `VAGA_LEITURA_TIMEOUT_SEGUNDOS` (15).

## Abordagem de Testes

### Testes Unidade

Seguem `testing-rules.md`: classes `TestNomeDaClasse`, sem comentários, blocos AAA separados, apenas `unittest.mock`.

- `TestLinkVaga`: normalização, remoção de rastreamento, id do LinkedIn em links diretos e de busca, esquemas inválidos, link sem id.
- `TestDadosVaga`: descrição vazia, limites de tamanho.
- `TestLeitorVagaLinkedInClient`: HTML de exemplo reduzido e anonimizado (fixture), como o `guest.html` real. Cobre campos completos, ausência de campos secundários, HTML sem título e respostas 429 e 404.
- `TestLeitorVagaGenericoClient`: JSON-LD válido, JSON-LD inválido, fallback para a IA.
- `TestExtratorDadosVagaIaClient`: cliente OpenAI falso, JSON inválido, valores fora de tipo, texto com instruções embutidas (não alteram o resultado).
- `TestClienteHttpSeguro` (`httpx.MockTransport` e resolvedor falso): IPs privados, loopback, metadados, redirecionamento para IP interno, excesso de redirecionamentos, tamanho e tempo.
- `TestLimitadorLeituraVagaEmMemoria`: limites por minuto e por dia, isolamento entre usuários.
- `TestExtrairDadosVaga` (fakes das portas): prioridade do texto, escolha de leitor por fonte, LinkedIn desligado, propagação de falhas, limite excedido.
- `TestVagaRepositoryImpl` e fake: gravação e leitura dos novos campos, linhas antigas com nulos. Usa `TEST_DATABASE_URL`.
- Roteador: `POST /vagas/extracoes` em 200, 422, 429, 502 e sem sessão (401). Testes de captura cobrem os campos novos.
- `test_arquitetura.py`: `lint-imports` continua passando.

### Testes de Serviço

Frontend (Vitest e MSW): `CampoLinkVaga`, preenchimento dos campos, estados de carregamento, erro e fallback para colar texto, nas duas telas. E2E (Playwright), com dublê do leitor em `tests/e2e/app_e2e.py`, sem rede real: link com sucesso e link com falha. `npm run gerar-tipos` e o commit do `schema.d.ts` mantêm o CI verde.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Objetos de valor e portas do domínio (`LinkVaga`, `DadosVaga`, exceções). Base de tudo e sem I/O.
2. Cliente HTTP seguro. Pré-requisito de qualquer leitor.
3. Extrator por IA e leitor genérico.
4. Leitor do LinkedIn.
5. Limitador e caso de uso `ExtrairDadosVaga`.
6. Endpoint, handlers, injeção e configuração.
7. Persistência da captura (migração, entidade, repositório, DTOs, schemas).
8. Frontend das duas telas.
9. E2E, documentação no `README.md` e `.env.example`.

### Dependências Técnicas

- `httpx` e `beautifulsoup4` já existem. Nenhuma biblioteca nova é necessária.
- Chave da OpenAI configurada para a extração por texto.
- Migração `0005` aplicada na subida da API (mecanismo existente).

## Monitoramento e Observabilidade

Logger `jobsync.vaga`, sem registrar conteúdo da vaga nem a URL completa:
- `INFO`: leitura concluída, com fonte, domínio, duração e campos preenchidos (lista de nomes).
- `WARNING`: leitura indisponível, com fonte, domínio, motivo (`bloqueado`, `nao_encontrada`, `tempo_esgotado`, `sem_dados`) e status HTTP; limite excedido, com o id do usuário.
- `WARNING`: tentativa de endereço recusado pela proteção SSRF, com o motivo.
- `ERROR`: falha inesperada do adapter ou resposta da IA inválida.

A taxa de sucesso por fonte (PRD, questão 2) sai desses logs agrupados por `fonte` e `motivo`.

## Considerações Técnicas

### Decisões Principais

- **Domínio `vaga`, adapters novos.** `vaga_externa` já importa `vaga`, e o contrato `acyclic_siblings` proíbe o caminho inverso. O `ExtratorTextoPaginaClient` atual permanece como está. A duplicação é uma busca HTTP, agora centralizada no cliente seguro, e o cliente antigo pode migrar depois.
- **Interpretação determinística no LinkedIn.** Evita custo de IA e alucinação. Se faltar título ou descrição, falha explicitamente em vez de pedir à IA que adivinhe.
- **Texto original, sem resumo.** A adaptação e o ATS dependem das palavras-chave.
- **Rascunho sem persistência**, como `/vagas/avaliacoes`.
- **Chave de desligamento** do LinkedIn, para retirar a fonte sem novo deploy de código.
- **Limitador em memória.** Simples e suficiente para o início. É reiniciado com o processo e multiplica o limite por número de workers.
- **Rejeitados:** navegador automatizado e contorno do desafio anti-bot (fragilidade e termos de uso), extensão (decisão do produto), OAuth do LinkedIn (não dá acesso a vagas), provedor pago (questão em aberto 3 do PRD).

### Riscos Conhecidos

- **Bloqueio por IP de servidor (429 ou desafio).** O teste inicial foi de uma máquina residencial. Mitigação: falha clara, fallback de colar o texto, medição pelos logs e chave de desligamento.
- **Termos de uso do LinkedIn proíbem acesso automatizado.** Risco aceito pelo responsável pelo produto e registrado no PRD. A fonte é marcada como experimental.
- **Mudança no HTML do LinkedIn.** O interpretador fica isolado em uma classe, com fixture. Quebra vira `LeituraVagaIndisponivel`, não dado errado.
- **SSRF e DNS rebinding.** Mitigação: conexão no IP já validado. Validado em experimento local (task 2.0): com a extensão `sni_hostname`, o `httpx` valida o certificado contra o nome original; sem ela, a verificação falha ("IP address mismatch"). Se uma versão futura do `httpx` deixar de respeitar a extensão, a falha é fechada (erro de rede), nunca uma abertura.
- **Injeção de instruções no texto da vaga.** Mitigação: prompt trata o texto como dado, sem ferramentas, com saída validada.
- **Dados pessoais de terceiros na página.** O parser só lê os campos pedidos e não guarda o restante.

### Conformidade com Padrões

- `back-end-general-rules.md`: URL com substantivo plural (`/vagas/extracoes`, como `/vagas/avaliacoes`); POST com 200 por não criar recurso; status específicos; erros RFC 7807 por handlers centrais; Pydantic nas entradas e saídas; contrato alterado só de forma aditiva e a pedido do PRD.
- `code-design-standards.md`: `domain` sem I/O (o `LinkVaga` usa só biblioteca padrão); casos de uso em `service_layer`; adapters implementam portas; injeção pela composição em `entrypoints`; nenhum domínio importa o `domain` de outro.
- `testing-rules.md`: nomes, AAA, sem comentários, `unittest.mock`, testes só pela API pública.
- `general-rules.md` e `AGENTS.md`: TDD, DRY, KISS, YAGNI, mudanças restritas ao pedido.
- `setup.cfg` (import-linter): camadas por domínio, ausência de ciclos e `domain` isolado.

Desvio: nenhum, exceto a duplicação consciente da busca HTTP descrita acima.

### Arquivos relevantes e dependentes

- `src/jobsync/vaga/domain/vaga.py`, `vaga_repository.py`
- `src/jobsync/vaga/adapters/vaga_repository_impl.py`, `vaga_repository_fake.py`, `job_description_analyzer_client.py` (padrão de prompt)
- `src/jobsync/vaga/service_layer/capturar_vaga/`
- `src/jobsync/vaga_externa/adapters/extrator_texto_pagina_client.py` (referência, sem alteração)
- `src/jobsync/shared_kernel/adapters/cliente_openai_client.py`, `persistence/migracoes/`
- `src/jobsync/entrypoints/api/routers/vaga_router.py`, `schemas/vaga.py`, `dependencies.py`, `exceptions.py`, `main.py`
- `src/jobsync/entrypoints/dependencies.py`, `servidor_captura.py` (sem alteração)
- `src/jobsync/tests/vaga/`, `tests/entrypoints/api/`, `tests/e2e/app_e2e.py`, `tests/test_arquitetura.py`
- `frontend/src/features/ajustar-vaga/AjustarVagaPage.tsx`, `vagas-salvas/ColarVagaModal.tsx`, `frontend/src/api/`
- `setup.cfg`, `.env.example`, `README.md`

# Adaptador de Currículo para Vagas (MVP)

Sistema de gestão de currículo e candidatura. Recebe um currículo em PDF,
uma descrição de vaga, e gera uma nova versão do currículo adaptada
(seção por seção) para aquela vaga, no idioma escolhido (Português/Inglês).

## Arquitetura

O projeto segue **Arquitetura Hexagonal (Ports and Adapters)** com **DDD**, com as
regras de negócio isoladas de qualquer framework ou biblioteca externa:

```
src/                        Código fonte da aplicação
  jobsync/                  Raiz do pacote da aplicação
    <dominio>/              Cada domínio de negócio encapsula suas próprias camadas
      domain/               Entidades, Value Objects, Ports (interfaces) - DENTRO do hexágono
      service_layer/        Casos de uso e DTOs - DENTRO do hexágono
      adapters/             Adapters concretos (implementações das portas) - FORA do hexágono

    shared_kernel/          Conceitos transversais compartilhados entre domínios
      domain/               Value Objects compartilhados (ex: NomeArquivo, CatalogoLocalizacao)
      adapters/             Mecanismos técnicos compartilhados (ex: ClienteOpenAI, ClienteJev, conexão SQLite)

    entrypoints/            Adapters de entrada da aplicação
      streamlit_app.py      Interface web (Streamlit)
      servidor_captura.py   API FastAPI para captura de vagas (extensão Chrome)
      dependencies.py       Composition Root / injeção de dependências

    tests/                  Testes unitários e de arquitetura espelhando src/jobsync/
      <dominio>/            Testes do domínio correspondente
      shared_kernel/        Testes dos conceitos transversais
      test_arquitetura.py   Validação dos contratos do import-linter

storage/                    PDFs gerados e banco SQLite são salvos aqui
sdd/                        Documentos de especificação e templates
```

**Fluxo de processamento por seção:** o PDF enviado é lido e segmentado pela
IA em seções reconhecidas (Tecnologias, Perfil, Experiências, Formação,
Certificações, Idiomas). Cada seção é então enviada individualmente à IA
para ser reescrita/priorizada conforme a vaga e traduzida para o idioma
alvo, preservando os fatos originais (empresas, datas, tecnologias). As
seções ajustadas são remontadas e um novo PDF é gerado.

## Pré-requisitos

- Python 3.10+
- Uma chave da OpenAI: https://platform.openai.com/api-keys
- Uma chave da TypeSafe AI (Jev) para as avaliações: https://docs.typesafe.ai/

## Instalação

O projeto usa um ambiente virtual padrão do Python. No Linux/macOS, prefira `python3`; no Windows, use `python`.

```bash
# 1. Criar o ambiente virtual
python -m venv venv          # Linux/macOS também aceitam .venv
# Windows: python -m venv venv

# 2. Ativar o ambiente
source venv/bin/activate     # Linux/macOS
# Windows: venv\Scripts\activate

# 3. Atualizar o pip e instalar as dependências
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Copiar o arquivo de variáveis de ambiente
cp .env.example .env
# Edite o .env e substitua pelas suas chaves da OpenAI e da TypeSafe AI
```

> No macOS, veja também `README-macos.md` para instruções específicas.

## Variáveis de ambiente (.env)

Após copiar `.env.example` para `.env`, o arquivo mínimo fica assim:

```env
# .env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-6-luna
TYPESAFE_API_KEY=sua_chave_aqui
TYPESAFE_MODEL=jev-1.14.0
```

Os valores são carregados em tempo de execução por `python-dotenv`; certifique-se de que o arquivo esteja na raiz do projeto.

- `OPENAI_API_KEY` / `OPENAI_MODEL`: provedor de geração de texto (extração, adaptação de seções, carta de apresentação e sugestões ATS). O modelo padrão é `gpt-6-luna`.
- `TYPESAFE_API_KEY` / `TYPESAFE_MODEL`: provedor de avaliações estruturadas (Jev). Sem essa chave, as avaliações automáticas ficam indisponíveis, mas a adaptação do currículo continua funcionando.

## Executando o MVP

```bash
PYTHONPATH=src streamlit run src/jobsync/entrypoints/streamlit_app.py
```

A interface abrirá em `http://localhost:8501`. Anexe o PDF do currículo,
cole a descrição da vaga, informe cargo e empresa, escolha o idioma e
clique em "Gerar currículo adaptado".

### Servidor de captura de vagas (extensão Chrome)

A funcionalidade de captura de vagas depende de um segundo processo, rodando
em paralelo ao Streamlit:

```bash
PYTHONPATH=src uvicorn jobsync.entrypoints.servidor_captura:app --port 8502
```

Esse servidor expõe `http://localhost:8502/api/vagas/capturar` e é usado
exclusivamente pela extensão do navegador.

### Servidor backend API (FastAPI)

Para subir o backend independente com documentação OpenAPI em `/docs`:

```bash
PYTHONPATH=src uvicorn jobsync.entrypoints.api.main:app --reload --port 8000
```

O backend fica disponível em `http://localhost:8000` e a documentação interativa
em `http://localhost:8000/docs`.

#### Endpoints de avaliação (Jev)

Além dos recursos existentes, a API expõe avaliações estruturadas via Jev, com
score geral de 0 a 100 e resultados por dimensão (score, nível e confiança):

- `POST /v1/vagas/avaliacoes` — avalia a descrição da vaga nas dimensões
  completude, clareza, relevância e inclusão. O texto não é persistido.
- `POST /v1/experiencias-profissionais/avaliacoes` — avalia uma experiência
  individual em relação a uma vaga-alvo nas dimensões clareza de escrita,
  qualidade/detalhe, aderência à vaga e consistência textual. O texto não é
  persistido nem alterado.

`POST /v1/curriculos/{id}/adaptacoes` também executa a avaliação da vaga antes
de adaptar e devolve os resultados em campos aditivos (`avaliacao_vaga`,
`status_avaliacao_vaga`, `avaliacoes_experiencias`). Quando a entrada vem de um
perfil estruturado, cada experiência é adaptada e avaliada individualmente;
para entrada somente em PDF, não há avaliação automática individual das
experiências. Um score baixo nunca bloqueia a adaptação e, se o Jev estiver
indisponível, o fluxo prossegue e sinaliza as avaliações como `indisponivel`.

Limitações: a dimensão `consistencia_textual` mede apenas coerência e
sustentação interna do texto — não é verificação factual externa.

## Rodando os testes (TDD)

O `pytest.ini` já configura os caminhos (`pythonpath = . src src/jobsync`), então basta rodar a partir da raiz do projeto:

```bash
pytest
```

Comandos úteis:

```bash
pytest -q                            # saída resumida
pytest -v                            # verboso
pytest src/jobsync/tests/curriculo   # testes de um domínio
pytest -k "tailor"                   # filtrar por nome de teste
```

Se preferir explicitar o `PYTHONPATH`:

```bash
PYTHONPATH=src pytest
```

Os testes de `domain/` e `service_layer/` são independentes de rede e de
chave de API (usam dublês de teste / fakes para as portas). Os testes de
adapters de PDF também não dependem de rede.

## Deploy com Docker

Para executar o backend de forma isolada, sem depender do Streamlit:

```bash
# 1. Construir a imagem
docker build -t job-sync-backend .

# 2. Subir o container
docker run -p 8000:8000 job-sync-backend
```

O backend estará disponível em `http://localhost:8000`, com documentação
interativa em `/docs` e health check em `/health`.

Para passar as chaves da OpenAI/TypeSafe ou outras variáveis de ambiente:

```bash
cp .env.example .env
# edite o .env com seus valores
docker run --env-file .env -p 8000:8000 job-sync-backend
```

## Lint de arquitetura

```bash
PYTHONPATH=src lint-imports
```

## Padrão de nome do arquivo gerado

```
nomeCompleto-AAAA-MM-DD-cargoDaVaga-empresa.pdf
```

Exemplo: `AdrianoJoaoTeixeiraFilho-2026-07-22-EngenheiroDeSoftwareSenior-TechCorp.pdf`

Os arquivos são salvos automaticamente em `storage/` além de disponíveis
para download pela interface.

## Limitações conhecidas do MVP

- Depende das APIs da OpenAI e da TypeSafe AI (requer internet e chaves de
  API); não é totalmente offline.
- A segmentação de seções depende da qualidade da extração de texto do
  PDF original — currículos com layout muito incomum ou PDFs escaneados
  (imagem sem OCR) podem não ser segmentados corretamente.
- O layout do PDF gerado é fixo (não é uma cópia do PDF original), gerado
  via reportlab a partir do conteúdo estruturado extraído.

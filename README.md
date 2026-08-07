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
      adapters/             Mecanismos técnicos compartilhados (ex: ClienteGroq, conexão SQLite)

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
- Uma chave gratuita da Groq: https://console.groq.com/keys

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
# Edite o .env e substitua pela sua chave da Groq
```

> No macOS, veja também `README-macos.md` para instruções específicas.

## Variáveis de ambiente (.env)

Após copiar `.env.example` para `.env`, o arquivo mínimo fica assim:

```env
# .env
GROQ_API_KEY=sua_chave_aqui
```

O valor é carregado em tempo de execução por `python-dotenv`; certifique-se de que o arquivo esteja na raiz do projeto e que a chave tenha sido gerada em <https://console.groq.com/keys>.

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

- Depende da API gratuita da Groq (requer internet e chave de API); não é
  totalmente offline.
- A segmentação de seções depende da qualidade da extração de texto do
  PDF original — currículos com layout muito incomum ou PDFs escaneados
  (imagem sem OCR) podem não ser segmentados corretamente.
- O layout do PDF gerado é fixo (não é uma cópia do PDF original), gerado
  via reportlab a partir do conteúdo estruturado extraído.

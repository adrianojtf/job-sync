# Instalação no macOS

As instruções do `README.md` são em grande parte compatíveis com o macOS, mas a versão abaixo traz os ajustes mais práticos para esse sistema, incluindo o uso de `python3` e a criação do arquivo `.env`.

## Pré-requisitos

- macOS com Python 3.10+ instalado
- Homebrew (recomendado) para instalar o Python, se necessário
- Uma chave gratuita da Groq: https://console.groq.com/keys

Se o `python3` ainda não estiver disponível, instale-o com:

```bash
brew install python@3.12
```

> Se o comando `python3` não estiver no PATH após a instalação, abra um novo terminal ou adicione o diretório do Homebrew ao seu shell.

## 1. Clonar o projeto

```bash
git clone <url-do-repositorio>
cd job-sync
```

## 2. Criar e ativar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Instalar dependências

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configurar a variável de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` e substitua o valor de exemplo pela sua chave da Groq:

```env
GROQ_API_KEY=sua_chave_aqui
```

## 5. Executar o MVP

```bash
PYTHONPATH=src streamlit run src/jobsync/entrypoints/streamlit_app.py
```

A interface abrirá em `http://localhost:8501`.

## 5.1. Executar o servidor de captura (extensão de navegador)

A funcionalidade de captura de vagas (extensão Chrome) depende de um segundo processo, rodando em paralelo ao Streamlit, que recebe o texto capturado da página:

```bash
PYTHONPATH=src uvicorn jobsync.entrypoints.servidor_captura:app --port 8502
```

Esse servidor expõe apenas `http://localhost:8502/api/vagas/capturar`, usado exclusivamente pela extensão — não é necessário abri-lo no navegador.

## 6. Rodar os testes

```bash
pytest
```

ou, explicitando o `PYTHONPATH`:

```bash
PYTHONPATH=src pytest
```

Se o comando `pytest` não for encontrado mesmo com o ambiente ativado, use:

```bash
PYTHONPATH=src ./.venv/bin/pytest
```

## 7. Lint de arquitetura

```bash
PYTHONPATH=src lint-imports
```

# Adaptador de Currículo para Vagas (MVP)

Sistema de gestão de currículo e candidatura. Recebe um currículo em PDF,
uma descrição de vaga, e gera uma nova versão do currículo adaptada
(seção por seção) para aquela vaga, no idioma escolhido (Português/Inglês).

## Arquitetura

O projeto segue **Arquitetura Hexagonal (Ports and Adapters)**, com as
regras de negócio isoladas de qualquer framework ou biblioteca externa:

```
domain/            Entidades e Value Objects puros (Curriculo, SecaoCurriculo, NomeArquivo)
application/        Casos de uso e Portas (interfaces)
  ports/              Interfaces que a aplicação depende (Dependency Inversion)
  use_cases/          Orquestração da lógica de negócio
infrastructure/      Adapters concretos (implementações das portas)
  extractors/          Leitura de PDF (pdfplumber) + segmentação via IA
  llm/                 Cliente Groq + ajuste de texto por seção
  pdf/                 Geração do PDF final (reportlab)
ui/                  Interface Streamlit (Composition Root)
storage/             PDFs gerados são salvos aqui
tests/               Testes unitários (TDD) das camadas domain e application
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

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edite o .env e cole sua GROQ_API_KEY
```

## Executando o MVP

```bash
streamlit run ui/app_streamlit.py
```

A interface abrirá em `http://localhost:8501`. Anexe o PDF do currículo,
cole a descrição da vaga, informe cargo e empresa, escolha o idioma e
clique em "Gerar currículo adaptado".

## Rodando os testes (TDD)

```bash
pytest tests/ -v
```

Os testes de `domain/` e `application/` são independentes de rede e de
chave de API (usam dublês de teste / fakes para as portas). O teste de
`infrastructure/pdf` também não depende de rede.

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

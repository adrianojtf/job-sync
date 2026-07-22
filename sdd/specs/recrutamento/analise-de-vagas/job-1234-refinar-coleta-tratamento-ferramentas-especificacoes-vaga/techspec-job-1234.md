# Especificação Técnica

## Resumo Executivo

Esta Tech Spec descreve a implementação da correção de refinamento da coleta e tratamento de ferramentas, tecnologias e especificações de vagas, conforme definido no PRD `prd-job-1234.md`. O objetivo é reduzir inferências indevidas de tecnologias como "Django" quando somente "Python" está explicitamente mencionado. A solução propõe adicionar um componente de análise de descrições de vaga que separa requisitos explícitos de inferências implícitas e fornece dados estruturados para os demais motores do sistema.

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `JobDescriptionAnalyzerPort` (nova porta de aplicação): interface para análise de texto de vaga e classificação de requisitos técnicos em explícitos, implícitos e ambíguos.
- `JobDescriptionAnalyzerGroq` (novo adapter em `infrastructure/llm`): implementação baseada na mesma infraestrutura de LLM já usada pelo sistema, com prompts controlados para extração de requisitos de vaga.
- `AjustadorTextoGroq` (existente): receptor de descrição de vaga estruturada e aprimorada para ajustar seções do currículo sem incentivar inferência incorreta de tecnologias.
- `AdaptarCurriculoParaVaga` (existente): caso de uso que orquestra a adaptação do currículo; deve aceitar a análise de descrição de vaga e repassar dados estruturados para o ajuste de cada seção.

Fluxo de dados proposto:
1. A interface de entrada (`ui/app_streamlit.py`) envia a descrição de vaga para o caso de uso.
2. `AdaptarCurriculoParaVaga` delega a análise da descrição de vaga para `JobDescriptionAnalyzerPort`.
3. O adaptador `JobDescriptionAnalyzerGroq` consulta `ClienteGroq` com prompts específicos para extrair:
   - tecnologias e frameworks explicitamente listados
   - mencões de experiência implícita que não devem ser promovidas a requisitos técnicos
   - classificações de confidence/ambiguidade
4. O resultado estruturado é usado por `AjustadorTextoGroq` para informar as instruções de ajuste sem gerar inferências falsas.

## Design de Implementação

### Interfaces Principais

Proposta de interface de aplicação:

```python
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class RequisitoTecnico:
    nome: str
    categoria: str
    tipo: str  # explicito | implicito | ambiguidade
    origem: str

@dataclass(frozen=True)
class AnaliseVaga:
    requisitos: Sequence[RequisitoTecnico]
    ambiguidade: Sequence[str]
    texto_original: str

class JobDescriptionAnalyzerPort:
    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        ...
```

### Modelos de Dados

- `AnaliseVaga` conterá:
  - `requisitos`: lista de tecnologias, linguagens, frameworks, bancos de dados e habilidades explicitamente mencionados.
  - `ambiguidade`: itens cuja extração depende de contexto e precisam ser validados manualmente.
  - `texto_original`: descrição de vaga inteira para auditoria.
- `RequisitoTecnico.tipo` deve ser uma enumeração ou string limitada a `"explicito"`, `"implicito"` e `"ambiguidade"`.
- O domínio não precisa alterar `Curriculo` diretamente. A análise de vaga será usada como entrada adicional em `AjustadorTextoPort`.

### Endpoints de API

Não há endpoints HTTP no MVP atual; a integração acontece internamente via aplicação Streamlit. O ponto de extensão será a interface de entrada do caso de uso `AdaptarCurriculoParaVaga`.

## Pontos de Integração

- `ui/app_streamlit.py`: manter a entrada de descrição de vaga, mas encaminhar a descrição para o novo serviço de análise antes de ajustar o currículo.
- `application/use_cases/adaptar_curriculo_para_vaga.py`: estender o caso de uso para receber o resultado de `JobDescriptionAnalyzerPort` e repassar informações estruturadas ao `AjustadorTextoPort`.
- `infrastructure/llm/cliente_groq.py`: reutilizar a classe existente para chamadas JSON ao modelo sem mudanças significativas.
- `infrastructure/llm/ajustador_texto_groq.py`: fortalecer o prompt com a análise de vaga estruturada, reduzindo ainda mais a chance de LLM inferir frameworks não mencionados.

## Abordagem de Testes

### Testes Unidade

- Criar testes para o novo adapter `JobDescriptionAnalyzerGroq` usando um cliente Groq falso/dublê que responda JSON pré-definido.
- Testar `AdaptarCurriculoParaVaga` com um fake de `JobDescriptionAnalyzerPort` para garantir que o fluxo de análise é invocado antes do ajuste de seções.
- Validar que `AjustadorTextoGroq` recebe a descrição de vaga estruturada e aplica a instrução correta para a seção de tecnologias.
- Testar os modelos de domínio `RequisitoTecnico` e `AnaliseVaga` para garantir consistência e imutabilidade.

### Testes de Serviço

- Não há um conjunto de testes de serviço separado no MVP, mas pode ser adicionada uma suíte de integração leve que simula o pipeline de `AdaptarCurriculoParaVaga` com um `ClienteGroq` de teste.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Definir o modelo de domínio de análise de vaga (`AnaliseVaga`, `RequisitoTecnico`) e a porta `JobDescriptionAnalyzerPort`.
2. Implementar o adapter `JobDescriptionAnalyzerGroq` em `infrastructure/llm`, com prompts para extrair explicitamente tecnologias, frameworks e bancos de dados e classificar inferências.
3. Adicionar testes de unidade para o adapter e para o caso de uso expandido.
4. Estender `AdaptarCurriculoParaVaga` para chamar a nova porta antes de ajustar cada seção do currículo.
5. Atualizar `AjustadorTextoGroq` para aceitar e utilizar o resultado estruturado da análise de vaga.
6. Validar manualmente com a vaga de exemplo do PRD e ajustar prompts conforme necessário para reduzir falsos positivos.

### Dependências Técnicas

- `ClienteGroq` e a chave `GROQ_API_KEY` são dependências obrigatórias para o adapter de análise de vaga.
- O projeto já depende de `groq` e `pdfplumber`; nenhuma nova dependência externa é necessária para esta correção.
- Como o MVP usa arquitetura hexagonal, a implementação deve permanecer desacoplada da UI e do mecanismo de geração de PDF.

## Monitoramento e Observabilidade

- Registrar logs no nível `INFO` para cada execução de análise de vaga, incluindo:
  - hash ou ID de requisição anônimo
  - se a descrição foi processada com sucesso
  - número de requisitos explícitos extraídos
  - número de itens ambíguos detectados
- Adicionar métricas básicas de observabilidade, como:
  - contagem de análises de descrição de vaga realizadas
  - taxa de falhas de análise
  - número de itens implícitos sinalizados
- Garantir que o log de análise não exponha dados sensíveis do candidato ou da vaga além do necessário.

## Considerações Técnicas

### Decisões Principais

- Reutilizar a infraestrutura LLM existente (`ClienteGroq`) para manter consistência com o MVP.
- Introduzir uma camada de análise de vaga isolada para separar a responsabilidade de extração de requisitos técnicos da lógica de ajuste de currículo.
- Manter o ajuste de currículo centrado em fatos originais; o novo componente apenas informa quais requisitos devem ser considerados "explícitos" ou "implícitos".
- Não realizar inferência automática de frameworks associados (como Django a partir de Python) sem confirmação explícita.

### Riscos Conhecidos

- O modelo LLM ainda pode gerar falsos positivos ou inferências ambíguas. Isso deve ser mitigado com prompts conservadores e classificações explícitas de confiança.
- A ausência de regras de `.windsurf/rules` no repositório significa que a conformidade de implementação deve ser documentada manualmente.
- O tempo de resposta e o custo de chamadas de LLM podem aumentar levemente devido à etapa adicional de análise de descrição de vaga.

### Conformidade com Padrões

Não foram encontradas regras em `/.windsurf/rules` no repositório atual. Esta Tech Spec, portanto, documenta o alinhamento com o padrão de arquitetura hexagonal existente (`application/ports`, `infrastructure/llm`, `ui/app_streamlit.py`) e presume a ausência de regras específicas a serem aplicadas.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/analise-de-vagas/job-1234-refinar-coleta-tratamento-ferramentas-especificacoes-vaga/prd-job-1234.md`
- `application/use_cases/adaptar_curriculo_para_vaga.py`
- `application/ports/ajustador_texto_port.py`
- `infrastructure/llm/ajustador_texto_groq.py`
- `infrastructure/llm/cliente_groq.py`
- `ui/app_streamlit.py`
- `infrastructure/extractors/extrator_curriculo_segmentado_ia.py`

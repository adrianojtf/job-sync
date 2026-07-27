# Especificação Técnica

## Resumo Executivo

Esta Tech Spec descreve a implementação da correção de localização e organização da seção de tecnologias no fluxo de geração de currículos em PDF, conforme definido no PRD `prd-job-0003.md`.

O objetivo é garantir que os rótulos de seções e as categorias de tecnologias sejam renderizados de forma consistente com o idioma selecionado pelo usuário, sem depender de valores fixos em português ou de uma estrutura de categorias inconsistente. A solução será aplicada no pipeline de geração de PDF, preservando o conteúdo do currículo e o fluxo atual de adaptação.

Status de implementação atual:
- O caso de uso `AdaptarCurriculoParaVaga` já recebe o `idioma_alvo` e repassa o currículo adaptado para a geração de PDF.
- `GeradorPdfReportLab` já aplica destaque visual a categorias de tecnologia, mas usa uma regra hard-coded com rótulos em inglês e não possui uma camada de localização explícita.
- O modelo de domínio `Curriculo` e `SecaoCurriculo` continua sendo usado sem alteração estrutural para esta correção.
- A lógica de tradução/organização de categorias não está centralizada, o que dificulta manutenção e expansão futura para outros idiomas.

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `AdaptarCurriculoParaVaga` (em `application/use_cases/adaptar_curriculo_para_vaga.py`): orquestra a extração do currículo, ajuste textual e geração do PDF. Deve passar o idioma de saída para o gerador.
- `GeradorPdfReportLab` (em `infrastructure/pdf/gerador_pdf_reportlab.py`): componente responsável por montar o PDF final com ReportLab. Será o ponto principal de alteração para localização e agrupamento visual das categorias.
- `Curriculo` e `SecaoCurriculo` (em `domain/curriculo.py`): modelos de domínio que representam o currículo e suas seções. Não serão alterados para introduzir lógica de tradução.
- `GeradorPdfPort` (em `application/ports/gerador_pdf_port.py`): interface de geração de PDF. Deve ser estendida para receber o idioma alvo do contexto de geração.
- `LocalizadorTexto` (novo componente opcional em `infrastructure/localizacao/` ou `infrastructure/pdf/`): camada dedicada a armazenar mapeamentos de rótulos por idioma e a aplicar fallback controlado.

Fluxo de dados proposto:
1. O caso de uso `AdaptarCurriculoParaVaga` recebe a solicitação com `idioma_alvo`.
2. O currículo já adaptado é repassado ao gerador de PDF junto com o idioma alvo.
3. O gerador consulta um catálogo de localização para traduzir rótulos de seções e categorias tecnológicas.
4. O PDF é montado com os rótulos corretos e a estrutura visual das categorias conforme o idioma selecionado.

## Design de Implementação

### Interfaces Principais

A interface do gerador de PDF será ajustada para receber o idioma alvo no momento da geração, sem alterar o domínio.

Exemplo de proposta:

```python
class GeradorPdfPort(ABC):
    @abstractmethod
    def gerar(self, curriculo: Curriculo, idioma_alvo: str) -> bytes:
        ...
```

A implementação em ReportLab consumirá esse idioma para escolher os rótulos corretos.

### Camada de Localização

Será criada uma camada de localização dedicada a centralizar os textos de apresentação usados no PDF.

Estrutura sugerida:

```python
@dataclass(frozen=True)
class CatalogoLocalizacao:
    secoes: dict[str, dict[str, str]]
    categorias_tecnologia: dict[str, dict[str, str]]
```

Mapeamentos mínimos:

- Seções:
  - pt: `Tecnologias`, `Perfil`, `Experiências`, `Formação`, `Certificações`, `Idiomas`
  - en: `Technologies`, `Profile`, `Experience`, `Education`, `Certifications`, `Languages`
- Categorias de tecnologia:
  - pt: `Linguagens`, `Frameworks`, `Desenvolvimento Web`, `DevOps`, `Bancos de Dados`, `Controle de Versão`, `Outros`
  - en: `Languages`, `Frameworks`, `Web Development`, `DevOps`, `Databases`, `Version Control`, `Other`

Fallback:
- Se um idioma não estiver mapeado, o sistema deve usar o idioma de entrada do currículo ou o idioma base do sistema, com fallback consistente para o português.
- Rótulos desconhecidos devem permanecer inalterados para evitar quebra de renderização.

### Renderização do PDF

A implementação do `GeradorPdfReportLab` deve aplicar o seguinte comportamento:

1. Traduzir os títulos das seções exibidas no PDF com base no idioma alvo.
2. Traduzir ou normalizar os rótulos de categorias de tecnologias na seção `Tecnologias`.
3. Preservar a estrutura lógica do conteúdo original (tecnologias, categorias e itens) sem alterar o texto factual do currículo.
4. Agrupar visualmente os itens de tecnologia sob as categorias apropriadas com rótulos localizados.
5. Manter o destaque visual já existente em negrito, mas agora aplicado sobre os rótulos localizados.

A implementação deve priorizar a compatibilidade com o layout atual do PDF e com a estrutura do conteúdo já existente no currículo. Não será necessário reestruturar o modelo de domínio ou mudar a lógica de adaptação textual para esta correção.

### Modelos de Dados

Não serão introduzidos novos modelos de domínio. O fluxo seguirá utilizando `Curriculo` e `SecaoCurriculo`.

A camada de localização será tratada como um componente de apresentação/infraestrutura, não como parte do domínio.

### Endpoints de API

Não há necessidade de alterar endpoints HTTP neste escopo. A correção é interna ao fluxo de geração de PDF.

## Pontos de Integração

- `application/ports/gerador_pdf_port.py`: alterar a assinatura de `gerar()` para receber o idioma alvo.
- `application/use_cases/adaptar_curriculo_para_vaga.py`: passar `solicitacao.idioma_alvo` ao gerador após o currículo ser adaptado.
- `infrastructure/pdf/gerador_pdf_reportlab.py`: principal ponto de alteração para:
  - traduzir rótulos de seções;
  - localizar categorias de tecnologia;
  - aplicar agrupamento visual consistente em português e inglês;
  - preservar o conteúdo original do currículo sem reescrita de fatos.
- `tests/test_gerador_pdf.py`: atualizar cenários existentes e adicionar cobertura para os dois idiomas suportados.

## Abordagem de Testes

### Testes Unidade

- Criar testes para o catálogo de localização verificando:
  - mapeamento correto para `pt` e `en`;
  - fallback para idioma desconhecido;
  - preservação de rótulos não mapeados.
- Atualizar o adapter `GeradorPdfReportLab` para validar que:
  - os títulos de seção do PDF são renderizados no idioma correto;
  - as categorias de tecnologia aparecem traduzidas;
  - o conteúdo factual do currículo não é alterado.
- Testar cenários com conteúdo já estruturado e com conteúdo sem categorias explícitas, garantindo que o renderizador não quebre.

### Testes de Integração

- Validar o fluxo completo em `AdaptarCurriculoParaVaga` para garantir que o idioma alvo é repassado corretamente ao gerador.
- Gerar PDF de exemplo em português e inglês e validar se os rótulos aparecem conforme esperado.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Definir o catálogo de localização e o fallback para `pt`/`en`.
2. Estender a porta `GeradorPdfPort` e adaptar `AdaptarCurriculoParaVaga` para repassar `idioma_alvo`.
3. Implementar a lógica de localização e agrupamento visual no `GeradorPdfReportLab`.
4. Adicionar testes unitários e de integração cobrindo português e inglês.
5. Validar manualmente o PDF gerado para garantir consistência visual e semântica.

### Dependências Técnicas

- O projeto já depende de `reportlab`, portanto não é necessária nova biblioteca para este escopo.
- A solução deve manter a separação entre domínio, aplicação e infraestrutura, sem introduzir lógica de tradução no modelo de domínio.

## Monitoramento e Observabilidade

- Não é necessário introduzir métricas específicas para esta correção.
- O fluxo de geração de PDF deve continuar registrando falhas e exceções de forma consistente com o comportamento atual.
- Em caso de idioma não mapeado, o sistema deve registrar um aviso de fallback para facilitar diagnóstico futuro.

## Considerações Técnicas

### Decisões Principais

- Centralizar os textos de apresentação em uma camada de localização para evitar hard-coding disperso.
- Manter a lógica de tradução no nível de apresentação, preservando o domínio e o fluxo atual.
- Preservar o conteúdo factual original do currículo e alterar apenas os rótulos e a organização visual das categorias.
- Utilizar fallback previsível para idiomas não suportados, preferindo consistência à tentativa de inferência agressiva.

### Riscos Conhecidos

- Rótulos de seção ou categoria podem aparecer inconsistentes se a lógica de tradução não for aplicada em todas as rotas de renderização.
- Estruturas de conteúdo pouco padronizadas podem exigir ajustes finos no parsing visual para evitar que categorias sejam renderizadas de forma inadequada.
- Alterações na assinatura de `GeradorPdfPort` podem impactar testes e implementações alternativas do port, exigindo atualização consistente.

### Conformidade com Padrões

A implementação deve seguir o padrão arquitetural hexagonal já adotado no projeto, mantendo a lógica de tradução em camada de infraestrutura/apresentação e sem introduzir dependência do domínio em detalhes de renderização de PDF.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/geracao-de-curriculo/job-0003-correcao-traducao-categorias-tecnologias/prd-job-0003.md`
- `application/use_cases/adaptar_curriculo_para_vaga.py`
- `application/ports/gerador_pdf_port.py`
- `infrastructure/pdf/gerador_pdf_reportlab.py`
- `domain/curriculo.py`
- `tests/test_gerador_pdf.py`

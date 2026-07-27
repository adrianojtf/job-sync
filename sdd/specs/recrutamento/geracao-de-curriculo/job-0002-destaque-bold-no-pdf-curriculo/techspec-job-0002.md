# Especificação Técnica

## Resumo Executivo

Esta Tech Spec define a implementação da correção de formatação do gerador de currículos em PDF, conforme descrito no PRD `prd-job-0002.md`. A solução propõe a aplicação de ênfase visual em campos de tecnologia, cabeçalhos de experiência e elementos de formação usando o mecanismo ReportLab existente, sem alterar a estrutura de dados do currículo ou o fluxo de processamento atual.

Status de implementação atual:
- O adapter `GeradorPdfReportLab` já aplica negrito inline em categorias de tecnologia, cabeçalhos de experiência e posições, além de títulos e categorias de formação.
- A lógica de marcação é restrita ao texto de apresentação do PDF e preserva o conteúdo original do currículo.
- O espaçamento extra entre blocos de experiência é inserido no fluxo de montagem do PDF.
- A validação automatizada em `tests/test_gerador_pdf.py` cobre as regras principais e confirma que o PDF gerado permanece válido.

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `GeradorPdfReportLab` (adapter em `infrastructure/pdf/gerador_pdf_reportlab.py`): componente responsável por montar o documento PDF final a partir do agregador de domínio `Curriculo`.
- `Curriculo` e `SecaoCurriculo` (em `domain/curriculo.py`): modelo de domínio que representa o currículo e suas seções independentes.
- `AdaptarCurriculoParaVaga` (caso de uso em `application/use_cases/adaptar_curriculo_para_vaga.py`): orquestra a extração do currículo, o ajuste de texto se necessário e a geração do PDF. O fluxo não muda para esta correção.

Fluxo de dados proposto:
1. O caso de uso `AdaptarCurriculoParaVaga` passa o `Curriculo` adaptado para o `GeradorPdfReportLab`.
2. `GeradorPdfReportLab` monta as seções em ordem e converte cada bloco de texto em objetos ReportLab `Paragraph`.
3. Antes de renderizar cada parágrafo, o adapter aplica formatação inline compatível com ReportLab para inserir negrito somente nos rótulos e cabeçalhos definidos.

## Design de Implementação

### Interfaces Principais

Não há necessidade de criar novas portas públicas para esta correção. A implementação ficará restrita ao adapter do gerador de PDF.

Proposta de helper interno para o adapter:

```python
from reportlab.platypus import Paragraph

class GeradorPdfReportLab(GeradorPdfPort):
    ...

    @staticmethod
    def _aplicar_enfase(conteudo: str) -> str:
        ...
```

### Modelos de Dados

Não serão introduzidos novos modelos de domínio. O currículo continuará a ser transportado pelo mesmo objeto `Curriculo` com suas `SecaoCurriculo` existentes.

As transformações serão aplicadas apenas ao texto de apresentação do PDF, preservando o conteúdo original de `secao.conteudo`.

### Endpoints de API

Nenhum endpoint HTTP ou interface pública adicional é necessário para esta correção. O ajuste é interno ao pipeline de geração de PDF.

## Pontos de Integração

- `infrastructure/pdf/gerador_pdf_reportlab.py`: principal ponto de alteração. O método `_formatar_conteudo` será estendido ou refatorado para:
  - detectar categorias na seção de Tecnologias e aplicar `<b>...</b>` apenas às etiquetas de categoria.
  - detectar a linha de cabeçalho de empresa+datas e a posição da experiência, aplicando negrito a ambos.
  - preservar as descrições de experiência como texto normal.
  - detectar títulos e categorias na seção de Formação acadêmica e aplicar negrito apenas aos elementos de destaque.
  - inserir espaçamento visual adicional entre cada experiência no PDF.
- `domain/curriculo.py`: permanece inalterado, garantindo que o modelo de domínio não seja modificado para atender à formatação de apresentação.
- `application/use_cases/adaptar_curriculo_para_vaga.py`: fluxo de orquestração do PDF continua igual, garantindo compatibilidade com currículos gerados anteriormente.

## Abordagem de Testes

### Testes Unidade

- Atualizar `tests/test_gerador_pdf.py` ou adicionar testes específicos para o adapter `GeradorPdfReportLab` verificando:
  - `GeradorPdfReportLab.gerar()` retorna bytes de PDF válidos diante de conteúdo de tecnologia, experiência e formação.
  - os parágrafos da seção de Tecnologias incluem o markup `<b>...</b>` somente nas etiquetas de categoria esperadas.
  - o parágrafo da experiência reconhece e negrita o cabeçalho de empresa+datas e o cargo/posição.
  - a seção de Formação acadêmica tem ênfase em títulos e categorias sem alterar datas e instituições.
  - existem blocos de espaçamento adicionais entre experiências quando o conteúdo contém múltiplas entradas.
- Usar textos de exemplo do PRD para cobrir os três padrões principais: tecnologias, experiências e formação.

### Testes de Serviço

- Não há necessidade de um teste de serviço separado além de validação manual do PDF gerado, já que a alteração é pontual no adapter de apresentação.
- Caso desejado, uma verificação de integração leve pode gerar um PDF de exemplo e confirmar que ele começa com `%PDF` e contém as partes esperadas no fluxo de montagem.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Refatorar ou estender `infrastructure/pdf/gerador_pdf_reportlab.py` para extrair um helper de formatação inline compatível com ReportLab.
2. Implementar regras de ênfase específicas para:
   - categorias de tecnologia (`Languages`, `Frameworks`, `Web Development`, `DevOps`, `Databases`, `Version Control`, `Other`);
   - cabeçalhos de experiência (empresa+período) e posição ocupada;
   - títulos/categorias na formação acadêmica.
3. Atualizar o rendering de conteúdo para inserir espaçamento extra entre blocos de experiência.
4. Adicionar testes unitários cobrindo as regras de estilo e a geração de PDF válida.
5. Validar manualmente o PDF com exemplos reais e ajustar a expressão de detecção para evitar ênfases excessivas.

### Dependências Técnicas

- `reportlab` já é dependência existente do projeto. Nenhuma nova biblioteca é necessária.
- A solução deve usar estilos e markup inline compatíveis com ReportLab `Paragraph`.

## Monitoramento e Observabilidade

- Não é necessário adicionar novos pontos de observabilidade apenas para esta correção de formatação.
- A implementação deve manter os logs existentes do pipeline de geração de PDF, se houver, e não introduzir chamadas externas adicionais.

## Considerações Técnicas

### Decisões Principais

- Manter a lógica de formatação no adapter de PDF para preservar a separação de responsabilidades entre domínio, caso de uso e apresentação.
- Usar markup inline ReportLab (`<b>...</b>`) em vez de alterar o modelo de domínio ou criar objetos textuais específicos de exibição.
- Preservar o conteúdo original do currículo como texto plano para evitar mudanças de semântica e permitir que a mesma fonte de dados continue servindo outros destinos além do PDF.
- Adotar um padrão conservador de detecção para evitar negritar texto que apenas contenha palavras-chave de forma incidental.

### Riscos Conhecidos

- Detecção demasiadamente liberal pode aplicar negrito em texto de descrição que não deve ser enfatizado.
- Uso incorreto de markup ReportLab pode quebrar a renderização de `Paragraph` se caracteres especiais não forem escapados corretamente.
- A lógica de formatação pode precisar de ajustes para suportar entradas com múltiplas linhas dentro de uma mesma seção ou variantes de pontuação.
- O comportamento de espaçamento extra entre experiências deve ser testado para não introduzir margens visuais excessivas.

### Conformidade com Padrões

Não foram encontradas regras em `/.windsurf/rules` no repositório atual. Esta Tech Spec documenta a conformidade com a arquitetura hexagonal existente, mantendo as modificações restritas ao adapter de apresentação PDF.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/geracao-de-curriculo/job-0002-destaque-bold-no-pdf-curriculo/prd-job-0002.md`
- `infrastructure/pdf/gerador_pdf_reportlab.py`
- `application/ports/gerador_pdf_port.py`
- `application/use_cases/adaptar_curriculo_para_vaga.py`
- `domain/curriculo.py`
- `tests/test_gerador_pdf.py`

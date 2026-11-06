# Tarefa 1.0: Fontes Carlito, RegistradorFontesPdf e EstiloCurriculoPdf

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Embarcar a família tipográfica Carlito no repositório e criar a base visual do novo layout: o registro das fontes no ReportLab e um objeto único com os tokens de estilo (cores, tamanhos, recuos) medidos no modelo de referência.

<requirements>
- Os 4 arquivos TTF da Carlito (Regular, Bold, Italic, BoldItalic) e o `OFL.txt` devem ficar em `src/jobsync/curriculo/adapters/pdf/fontes/`.
- `RegistradorFontesPdf.registrar()` deve registrar a família com `registerFontFamily`, para que `<b>` e `<i>` funcionem dentro de `Paragraph`.
- O registro deve ser idempotente (chamar duas vezes não falha nem registra de novo).
- Sem os arquivos TTF, o registrador deve usar Helvetica e emitir `logger.warning`, sem lançar exceção.
- `EstiloCurriculoPdf` deve ser um dataclass frozen com os tokens da tabela "Visão Geral dos Componentes" da techspec.
- `EstiloCurriculoPdf` deve expor os `ParagraphStyle` usados pelo gerador (nome, contato, título de seção, rótulo/corpo, empresa, período, cargo, tópico, contexto).
- Nenhuma dependência nova em `requirements*.txt`.
</requirements>

## Subtarefas

- [ ] 1.1 Copiar os TTF da Carlito (pacote `fonts-crosextra-carlito` ou repositório `googlefonts/carlito`) e o `OFL.txt` para `adapters/pdf/fontes/`.
- [ ] 1.2 Criar o pacote `src/jobsync/curriculo/adapters/pdf/` com `__init__.py`.
- [ ] 1.3 Escrever os testes de `RegistradorFontesPdf` (red).
- [ ] 1.4 Implementar `RegistradorFontesPdf` com retorno da família efetiva (Carlito ou Helvetica).
- [ ] 1.5 Implementar `EstiloCurriculoPdf` com os tokens e a fábrica de `ParagraphStyle`, recebendo a família de fontes.

## Detalhes de Implementação

Consultar em `techspec-job-0016.md`:
- "Visão Geral dos Componentes" (tabela de medidas e componentes novos).
- "Pontos de Integração" (registro de fontes e fallback).

## Critérios de Sucesso

- PDF gerado com o estilo usa fontes `Carlito-*` embutidas (verificável com `pdfplumber`).
- Ambiente sem os TTF continua gerando PDF com Helvetica.
- Tokens de cor e tamanho iguais aos do modelo: `#1F3864`, `#595959`, `#0563C1`, 16/11/11,5/10,5/10 pt.

## Testes da Tarefa

- [ ] `TestRegistradorFontesPdf`: registra a família Carlito quando os arquivos existem.
- [ ] `TestRegistradorFontesPdf`: retorna Helvetica quando o diretório não existe (usar `tmp_path`).
- [ ] `TestRegistradorFontesPdf`: segunda chamada não falha e retorna a mesma família.
- [ ] `TestEstiloCurriculoPdf`: estilo do tópico tem `leftIndent=36` e `bulletIndent=18`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/pdf/__init__.py` (novo)
- `src/jobsync/curriculo/adapters/pdf/registrador_fontes_pdf.py` (novo)
- `src/jobsync/curriculo/adapters/pdf/estilo_curriculo_pdf.py` (novo)
- `src/jobsync/curriculo/adapters/pdf/fontes/` (novo)
- `src/jobsync/tests/curriculo/test_registrador_fontes_pdf.py` (novo)
- `src/jobsync/tests/curriculo/test_estilo_curriculo_pdf.py` (novo)
- `Dockerfile` (referência: `COPY src/` já inclui as fontes)

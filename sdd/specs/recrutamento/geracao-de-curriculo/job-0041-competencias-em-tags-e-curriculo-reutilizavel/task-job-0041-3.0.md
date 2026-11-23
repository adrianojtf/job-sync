# Tarefa 3.0: Gerador de PDF com rótulo de categoria genérico

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Hoje `_negritar_categorias_tecnologia` e `_quebrar_categorias` só reconhecem rótulos do catálogo `categorias_tecnologia`. Com categorias criadas ou renomeadas pelo usuário, o rótulo não sairia em negrito. Esta tarefa torna o destaque genérico, sem mudar o layout.

<requirements>
- Cada linha da seção de tecnologias é uma categoria; o texto antes do primeiro ":" sai em negrito, qualquer que seja o rótulo.
- Rótulos do catálogo continuam traduzidos para o idioma alvo.
- Rótulos fora do catálogo saem como digitados.
- Linha sem ":" sai sem negrito.
- O layout do PDF não muda.
</requirements>

## Subtarefas

- [x] 3.1 Testes do gerador de PDF: rótulo customizado em negrito, uma categoria por linha, rótulo do catálogo traduzido, linha sem ":" (red).
- [x] 3.2 Alterar `_negritar_categorias_tecnologia` e `_linhas_de_tecnologias` (green).
- [x] 3.3 `_quebrar_categorias` foi mantido: um teste existente cobre textos antigos com várias categorias em uma linha só.
- [x] 3.4 Refatorar.

## Detalhes de Implementação

Techspec: "Decisões Principais" (rótulo genérico no PDF) e "Riscos Conhecidos" (layout de referência). PRD: RF 6.

## Critérios de Sucesso

- Categoria nova ou renomeada aparece em negrito no PDF.
- Testes existentes de `test_gerador_pdf_client.py` continuam passando.

## Testes da Tarefa

- [x] Testes de unidade do gerador de PDF.
- [x] Regressão: `src/jobsync/tests/curriculo/test_gerador_pdf_client.py`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/gerador_pdf_client.py`
- `src/jobsync/shared_kernel/domain/catalogo_localizacao.py`
- `src/jobsync/tests/curriculo/test_gerador_pdf_client.py`

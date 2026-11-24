# Tarefa 1.0: Rótulos dos quatro blocos no shared_kernel e convenção de texto do PDF

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cria a fonte única dos rótulos dos quatro blocos (pt e en, com apelidos reconhecidos) e estende a convenção de texto que o gerador de PDF lê e desenha.

<requirements>
- Enum `BlocoExperiencia` (contexto, responsabilidades, realizações, skills) com rótulos em pt e en e apelidos reconhecidos (ex.: "Key Achievements", "Principais entregas"), em `shared_kernel/domain/rotulos_blocos_experiencia.py`.
- `curriculo/domain/rotulos_experiencia.py` passa a derivar do módulo novo, sem mudar o comportamento atual de `rotulo_contexto`.
- `InterpretadorExperiencias` trata o rótulo como cabeçalho de bloco; bullets seguintes pertencem ao bloco aberto; `Technologies:` usa `|` como separador (PRD RF 26 a 30).
- Texto antigo continua legível: bullets sem cabeçalho viram realizações; `Context:` continua reconhecido.
- `estilo_curriculo_pdf` desenha os quatro blocos na ordem contexto, responsabilidades, realizações, skills; bloco vazio não deixa rótulo solto nem linha vazia.
- Rótulos traduzidos conforme o idioma (en: Context, Key Responsibilities, Key Achievements, Technologies; pt: Contexto, Principais responsabilidades, Principais realizações, Tecnologias).
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 1.1 Escrever os testes dos rótulos e do `InterpretadorExperiencias` (red).
- [ ] 1.2 Implementar `rotulos_blocos_experiencia` e adaptar `rotulos_experiencia` (green).
- [ ] 1.3 Estender o interpretador e o estilo do PDF para os quatro blocos (green).
- [ ] 1.4 Refatorar e rodar `tests/curriculo`.

## Detalhes de Implementação

Techspec: "Modelos de Dados" (Convenção de texto do PDF), "Visão Geral dos Componentes" e "Ordem de Construção" (passo 1). PRD: RF 26 a 30.

Complexidade: medium. Dependências: nenhuma.

## Critérios de Sucesso

- Texto com os quatro rótulos em pt e en é interpretado e desenhado na ordem correta.
- Os testes atuais de contexto e de PDF continuam verdes (sem regressão da JOB-0035).

## Testes da Tarefa

- [ ] Testes de `TestRotulosBlocosExperiencia` (pt, en, apelidos, caixa).
- [ ] Testes de `TestInterpretadorExperiencias` (blocos, bullets sem cabeçalho, bloco vazio).
- [ ] Testes de `TestEstiloCurriculoPdf`.
- [ ] Regressão: `src/jobsync/tests/curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/shared_kernel/domain/rotulos_blocos_experiencia.py (novo)`
- `src/jobsync/curriculo/domain/rotulos_experiencia.py`
- `src/jobsync/curriculo/adapters/pdf/interpretador_experiencias.py`
- `src/jobsync/curriculo/adapters/pdf/estilo_curriculo_pdf.py`
- `src/jobsync/curriculo/adapters/gerador_pdf_client.py`
- `src/jobsync/tests/curriculo/test_interpretador_experiencias.py`
- `src/jobsync/tests/curriculo/test_estilo_curriculo_pdf.py`
- `src/jobsync/tests/curriculo/test_gerador_pdf_client.py`

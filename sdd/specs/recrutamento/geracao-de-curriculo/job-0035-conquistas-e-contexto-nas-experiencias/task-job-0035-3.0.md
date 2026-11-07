# Tarefa 3.0: Gerador de PDF e prompt da fonte PDF

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Desenhar o contexto em itálico cinza e instruir o padrão no texto da seção de experiências vinda de PDF.

<requirements>
- Estilo `contexto` (`Helvetica-Oblique`, cor `#666666`) e reconhecimento de linha que comece com um rótulo conhecido, sem diferenciar maiúsculas, antes da regra do negrito da segunda linha.
- Sem rótulo solto nem linhas vazias quando faltar conquista ou contexto.
- Prompt de EXPERIENCIAS em `AjustadorTextoClient`: manter cabeçalho, bullets com "-" e linha final `Contexto:`/`Context:` por idioma; mesma regra de métricas.
- Complexidade: medium. Dependências: 1.0.
</requirements>

## Subtarefas

- [ ] 3.1 Testes do gerador com `pdfplumber` e do prompt (Red).
- [ ] 3.2 Estilo e reconhecimento.
- [ ] 3.3 Prompt da fonte PDF.

## Detalhes de Implementação

Ver "Gerador de PDF" em `techspec-job-0035.md`.

## Critérios de Sucesso

- Contexto sai oblíquo e cinza depois dos bullets.
- Contexto logo após o cabeçalho não vira negrito.

## Testes da Tarefa

- [ ] Testes de unidade do gerador e do ajustador de texto.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/gerador_pdf_client.py`
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`

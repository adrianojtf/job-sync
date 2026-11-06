# Resumo de Tarefas de Implementação do Layout do PDF de Currículo (JOB-0016)

## Tarefas

- [x] 1.0 Fontes Carlito, `RegistradorFontesPdf` e `EstiloCurriculoPdf`
- [ ] 2.0 `InterpretadorExperiencias` e `BlocoExperiencia`
- [ ] 3.0 `CatalogoLocalizacao`: título "Technical Skills" e rótulo de contexto
- [ ] 4.0 `GeradorPdfClient`: página, cabeçalho, títulos de seção, tecnologias e perfil
- [ ] 5.0 `GeradorPdfClient`: experiências com empresa/período, cargo, tópicos e contexto
- [ ] 6.0 `GeradorPdfClient`: formação, certificações e idiomas
- [ ] 7.0 Prompts de IA: preservar quebras de linha e tópicos `-`
- [ ] 8.0 Validação visual contra o modelo, suíte completa e `lint-imports`

## Status

- Tarefa 1.0 concluída.
- Execução das demais tarefas em pausa, aguardando a execução do JOB-0035. Escopo ajustado ao JOB-0035 (ver `techspec-job-0016.md`, seção "Relação com o JOB-0035").

## Dependências

- 1.0, 3.0 e 7.0 não dependem de nenhuma outra tarefa e podem ser feitas em paralelo.
- 3.0 deve ser concluída antes de 2.0 (o interpretador usa `rotulos_contexto()`).
- 1.0 e 3.0 devem ser concluídas antes de 4.0.
- 2.0 e 4.0 devem ser concluídas antes de 5.0.
- 5.0 deve ser concluída antes de 6.0.
- 1.0 a 7.0 devem ser concluídas antes de 8.0.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Fontes e estilo | low | — | `TestRegistradorFontesPdf`: registra Carlito; fallback Helvetica com diretório inexistente; registro idempotente |
| 2.0 | Interpretador de experiências | medium | 3.0 | `TestInterpretadorExperiencias`: empresa/período, formato `Cargo — Empresa (Período)`, sem período, tópicos `-`/`•`/`●`, contexto, formação, nenhuma linha perdida |
| 3.0 | Catálogo de rótulos | low | — | `Technical Skills` em inglês; `rotulo_contexto` e `rotulos_contexto`; fallback de idioma |
| 4.0 | Cabeçalho, títulos, tecnologias, perfil | medium | 1.0, 3.0 | Nome centralizado em caixa alta (Carlito-Bold 16, `#1F3864`); título em caixa alta + linha; uma categoria por linha |
| 5.0 | Experiências | high | 2.0, 4.0 | `●` em x ≈ 63 pt e continuação em x ≈ 81 pt; período com x1 ≈ 513 pt e cor `#595959`; cargo itálico azul; ordem do texto extraído |
| 6.0 | Formação, certificações, idiomas | medium | 5.0 | Instituição negrito + período à direita; curso em itálico azul; idioma em negrito por linha |
| 7.0 | Prompts de IA (extrator, regra geral e tecnologias) | low | — | Prompts enviados ao `ClienteOpenAI` (mock) contêm as regras de preservação de tópicos e linhas |
| 8.0 | Validação final | low | 1.0 a 7.0 | Suíte `pytest` verde; `lint-imports` sem quebra; comparação visual lado a lado anexada ao PR |

## Entregáveis principais

- PDF gerado com o mesmo estilo e design de `modelo-referencia-curriculo-en.pdf` (fonte Carlito, paleta azul-marinho/cinza, títulos em caixa alta com linha).
- Tópicos `-` renderizados com marcador `●` e recuo pendente.
- Empresa e período na mesma linha, com o período alinhado à direita.
- Prompts de extração e ajuste por IA preservando quebras de linha e tópicos, para que o gerador receba a estrutura correta.
- Nenhuma mudança na porta `GeradorPdfPort`, no agregado `Curriculo` ou nos endpoints.

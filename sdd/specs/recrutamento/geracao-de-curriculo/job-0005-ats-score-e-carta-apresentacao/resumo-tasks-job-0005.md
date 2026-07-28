# Resumo de Tarefas de Implementação de ATS Score e Carta de Apresentação

## Tarefas

- [x] 1.0 Modelar ResultadoAtsScore e implementar CalcularAtsScore com testes unitários
- [x] 2.0 Adicionar campo analise_vaga a ResultadoAdaptacao e ajustar testes existentes
- [x] 3.0 Definir porta GeradorCartaApresentacaoPort
- [x] 4.0 Implementar adapter GeradorCartaApresentacaoGroq com testes
- [x] 5.0 Implementar use case GerarCartaApresentacao com testes
- [x] 6.0 Integrar ATS Score e carta de apresentação na UI Streamlit
- [x] 7.0 Validação manual end-to-end e execução da suíte completa de testes

## Dependências

- 1.0 e 2.0 podem ser feitas em paralelo (não dependem uma da outra).
- 3.0 não depende de nenhuma outra tarefa desta lista.
- 3.0 deve ser concluída antes de 4.0.
- 2.0 e 4.0 devem ser concluídas antes de 5.0.
- 1.0 e 5.0 devem ser concluídas antes de 6.0.
- 6.0 deve ser concluída antes de 7.0.

## Entregáveis principais

- Cálculo de ATS Score (nota 0-100 + requisitos faltantes) reaproveitando a `AnaliseVaga` já extraída no fluxo existente, sem nova chamada de IA.
- `ResultadoAdaptacao` estendido para expor a `AnaliseVaga` usada, sem quebrar o fluxo atual de `AdaptarCurriculoParaVaga`.
- Geração de carta de apresentação personalizada via Groq, reaproveitando o mesmo padrão de porta/adapter já usado para ajuste de texto.
- Tela de resultado no Streamlit exibindo nota, requisitos faltantes e botão de download da carta, junto do PDF já gerado.

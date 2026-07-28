# Tarefa 2.0: Adicionar campo analise_vaga a ResultadoAdaptacao

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Estender o dataclass `ResultadoAdaptacao` (retornado por `AdaptarCurriculoParaVaga.executar`) para expor a `AnaliseVaga` já calculada internamente, permitindo que a Fase 1 reaproveite essa análise sem recalculá-la via IA.

<requirements>
- Adicionar campo `analise_vaga: AnaliseVaga` a `ResultadoAdaptacao` em `application/use_cases/adaptar_curriculo_para_vaga.py`.
- Preencher esse campo com o valor já calculado dentro de `executar` (a `AnaliseVaga` retornada por `self._analisador_vaga.analisar(...)`).
- Mudança aditiva: não alterar a assinatura de `executar`, nem o comportamento de geração do PDF — complexidade: low.
- Ajustar `tests/application/test_adaptar_curriculo_para_vaga.py` onde `ResultadoAdaptacao` for construído ou verificado.
</requirements>

## Subtarefas

- [x] 2.1 Adicionar o campo `analise_vaga: AnaliseVaga` ao dataclass `ResultadoAdaptacao`.
- [x] 2.2 Preencher o campo no retorno de `AdaptarCurriculoParaVaga.executar`.
- [x] 2.3 Revisar e ajustar `tests/application/test_adaptar_curriculo_para_vaga.py` para o novo campo.

## Detalhes de Implementação

Consultar a seção "Pontos de Integração" de `techspec-job-0005.md`: o campo deve ser preenchido com o mesmo valor já obtido na linha onde `analise_vaga = self._analisador_vaga.analisar(solicitacao.descricao_vaga)` ocorre em `adaptar_curriculo_para_vaga.py`, sem uma segunda chamada.

## Critérios de Sucesso

- `ResultadoAdaptacao.analise_vaga` reflete exatamente a mesma `AnaliseVaga` usada internamente para ajustar as seções do currículo.
- Nenhuma regressão nos testes existentes de `AdaptarCurriculoParaVaga`.

## Testes da Tarefa

- [x] Teste unitário: `ResultadoAdaptacao.analise_vaga` é igual à `AnaliseVaga` retornada pelo fake de `JobDescriptionAnalyzerPort`.
- [x] Suíte existente de `test_adaptar_curriculo_para_vaga.py` continua passando.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `application/use_cases/adaptar_curriculo_para_vaga.py`
- `tests/application/test_adaptar_curriculo_para_vaga.py`

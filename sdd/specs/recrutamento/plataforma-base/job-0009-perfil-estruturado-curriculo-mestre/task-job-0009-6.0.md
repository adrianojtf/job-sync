# Tarefa 6.0: Estender AdaptarCurriculoParaVaga/AnalisarAtsVaga/CandidatarNaVagaExterna com curriculo_pre_montado

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Adicionar um campo opcional `curriculo_pre_montado: Curriculo | None = None` ao InputDto dos três use cases existentes que hoje sempre extraem o currículo de um PDF via IA. Quando presente, o use case usa esse `Curriculo` diretamente, pulando a chamada a `ExtratorCurriculoPort`.

<requirements>
- `AdaptarCurriculoParaVagaInputDto`, `AnalisarAtsVagaInputDto`, `CandidatarNaVagaExternaInputDto`: `pdf_curriculo` passa a ser `bytes | None = None` (antes obrigatório); novo campo `curriculo_pre_montado: Curriculo | None = None`.
- Em cada `use_case.py`: `curriculo_original = input_dto.curriculo_pre_montado if input_dto.curriculo_pre_montado is not None else self._extrator.extrair(input_dto.pdf_curriculo)`.
- Em cada `validator.py`: exigir `pdf_curriculo` OU `curriculo_pre_montado` (não mais só `pdf_curriculo`); se nenhum dos dois for informado, levantar `ValueError`.
- Nenhuma mudança de comportamento quando `curriculo_pre_montado` não é informado (compatibilidade total com o código/testes já existentes).
- Complexidade: medium (mudança repetida em três use cases, cuidado para não quebrar nenhum teste existente).
</requirements>

## Subtarefas

- [ ] 6.1 Estender `AdaptarCurriculoParaVagaInputDto`/`validator.py`/`use_case.py` com `curriculo_pre_montado`.
- [ ] 6.2 Estender `AnalisarAtsVagaInputDto`/`validator.py`/`use_case.py` com `curriculo_pre_montado`.
- [ ] 6.3 Estender `CandidatarNaVagaExternaInputDto`/`validator.py`/`use_case.py` com `curriculo_pre_montado`.
- [ ] 6.4 Para cada um dos três use cases, adicionar um teste confirmando que, com `curriculo_pre_montado` informado, `ExtratorCurriculoPort.extrair` NUNCA é chamado (usar um fake que registra chamadas, ou que lança exceção se chamado).
- [ ] 6.5 Rodar a suíte completa e confirmar que nenhum teste existente quebrou.

## Detalhes de Implementação

Consultar a seção "Interfaces Principais" (exemplo de `AdaptarCurriculoParaVagaInputDto` modificado) de `techspec-job-0009.md`.

## Critérios de Sucesso

- Os três use cases aceitam `curriculo_pre_montado` e, quando informado, não chamam `ExtratorCurriculoPort`.
- Todos os testes já existentes desses três use cases (via `pdf_curriculo`) continuam passando sem modificação.

## Testes da Tarefa

- [ ] Teste unitário (um por use case): com `curriculo_pre_montado` informado, o extrator fake não é chamado, e o resultado usa esse currículo diretamente.
- [ ] Teste unitário (um por use case): sem `pdf_curriculo` nem `curriculo_pre_montado`, levanta `ValueError`.
- [ ] Suíte completa dos três use cases (testes já existentes) continua 100% passando.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/application/use_cases/adaptar_curriculo_para_vaga/dtos.py`
- `src/application/use_cases/adaptar_curriculo_para_vaga/validator.py`
- `src/application/use_cases/adaptar_curriculo_para_vaga/use_case.py`
- `src/application/use_cases/analisar_ats_vaga/dtos.py`
- `src/application/use_cases/analisar_ats_vaga/validator.py`
- `src/application/use_cases/analisar_ats_vaga/use_case.py`
- `src/application/use_cases/candidatar_na_vaga_externa/dtos.py`
- `src/application/use_cases/candidatar_na_vaga_externa/validator.py`
- `src/application/use_cases/candidatar_na_vaga_externa/use_case.py`
- `src/tests/application/use_cases/adaptar_curriculo_para_vaga/test_use_case.py`
- `src/tests/application/use_cases/analisar_ats_vaga/test_use_case.py`
- `src/tests/application/use_cases/candidatar_na_vaga_externa/test_use_case.py`

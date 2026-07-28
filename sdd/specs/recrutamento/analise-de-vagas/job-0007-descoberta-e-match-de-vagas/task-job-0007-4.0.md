# Tarefa 4.0: Implementar use case DescobrirVagasComMatch

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o use case que orquestra a busca paralela nas cinco fontes, deduplica os resultados e calcula o score de match de cada vaga contra o currículo escolhido, reaproveitando `CalcularAtsScore` (Fase 1) e `JobDescriptionAnalyzerPort` (existente).

<requirements>
- `DescobrirVagasComMatch.executar(termo: str, pdf_curriculo: bytes) -> tuple[VagaComScore, ...]`.
- Extrai o `Curriculo` uma única vez (via `ExtratorCurriculoPort`), não por vaga.
- Dispara as cinco buscas em paralelo (`ThreadPoolExecutor`), timeout individual de 8s (15s para Google Custom Search); falha/timeout de uma fonte não interrompe as demais.
- Deduplica por `(titulo.lower(), empresa.lower())`.
- Para cada vaga restante: analisa a descrição (`JobDescriptionAnalyzerPort`) e calcula o score (`CalcularAtsScore`).
- Retorna lista ordenada por `ResultadoAtsScore.nota` decrescente.
- Não chama nenhum outro use case diretamente (regra do projeto) — depende apenas de portas e do Domain Service `CalcularAtsScore`.
- Complexidade: medium.
</requirements>

## Subtarefas

- [ ] 4.1 Criar pacote `src/application/use_cases/descobrir_vagas_com_match/` (`use_case.py`, `__init__.py` — sem DTO, mesmo padrão de `EntrarOuCriarPerfil`, já que `executar` recebe apenas `termo` e `pdf_curriculo`).
- [ ] 4.2 Implementar a orquestração de busca paralela com `ThreadPoolExecutor` e tratamento de timeout/falha por fonte.
- [ ] 4.3 Implementar a deduplicação por título+empresa.
- [ ] 4.4 Implementar o cálculo de score por vaga e a ordenação decrescente do resultado.
- [ ] 4.5 Escrever testes usando fakes de `BuscadorVagasExternoPort` (um por fonte), cobrindo deduplicação, ordenação e resiliência a falha de uma fonte.

## Detalhes de Implementação

Consultar as seções "Fluxo de dados proposto" e "Interfaces Principais" de `techspec-job-0007.md`. Seguir o estilo de orquestração já usado em `AnalisarAtsVaga` (Fase 1) para reaproveitamento direto de portas.

## Critérios de Sucesso

- `DescobrirVagasComMatch.executar` retorna vagas únicas, ordenadas por score decrescente, mesmo quando uma ou mais fontes falham.

## Testes da Tarefa

- [ ] Teste unitário: deduplicação remove vagas com mesmo título+empresa vindas de fontes diferentes.
- [ ] Teste unitário: ordenação por score decrescente.
- [ ] Teste unitário: falha/timeout de uma fonte não impede o retorno das demais.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/application/use_cases/descobrir_vagas_com_match/dtos.py`
- `src/application/use_cases/descobrir_vagas_com_match/use_case.py`
- `src/application/use_cases/descobrir_vagas_com_match/validator.py`
- `src/application/use_cases/descobrir_vagas_com_match/__init__.py`
- `src/tests/application/use_cases/descobrir_vagas_com_match/test_use_case.py`

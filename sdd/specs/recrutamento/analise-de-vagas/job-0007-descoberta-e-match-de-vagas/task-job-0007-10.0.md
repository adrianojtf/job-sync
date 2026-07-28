# Tarefa 10.0: Estender BuscadorVagasExternoPort com parâmetro dias_maximo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Estender a porta `BuscadorVagasExternoPort.buscar` com um parâmetro opcional `dias_maximo`, usado nativamente apenas pela Adzuna (via `max_days_old` na query string); as demais fontes o recebem mas ignoram, já que o filtro delas acontece depois, no use case (Tarefa 11.0).

<requirements>
- `BuscadorVagasExternoPort.buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]`.
- Todos os adapters existentes (`BuscadorRemoteOk`, `BuscadorWeWorkRemotely`, `BuscadorArbeitnow`, `BuscadorGoogleCustomSearch`) atualizam a assinatura para aceitar `dias_maximo` e simplesmente ignoram o valor.
- `BuscadorAdzuna`: quando `dias_maximo is not None`, adiciona `max_days_old={dias_maximo}` aos parâmetros da requisição HTTP; quando `None`, omite o parâmetro (comportamento atual preservado).
- Complexidade: low.
</requirements>

## Subtarefas

- [ ] 10.1 Atualizar a assinatura de `BuscadorVagasExternoPort.buscar` com o novo parâmetro.
- [ ] 10.2 Atualizar a assinatura de todos os adapters existentes (ignorando o parâmetro, exceto Adzuna).
- [ ] 10.3 Implementar o uso de `max_days_old` em `BuscadorAdzuna` quando `dias_maximo` for informado.
- [ ] 10.4 Teste confirmando que `dias_maximo` é repassado como `max_days_old` na query string da Adzuna quando informado, e omitido quando `None`.

## Detalhes de Implementação

Consultar a seção "Interfaces Principais" (assinatura atualizada de `BuscadorVagasExternoPort`) de `techspec-job-0007.md`.

## Critérios de Sucesso

- A porta e todos os adapters aceitam `dias_maximo` sem quebrar o comportamento existente quando `None` (comportamento padrão, equivalente ao atual).
- `BuscadorAdzuna` usa `max_days_old` corretamente quando `dias_maximo` é informado.

## Testes da Tarefa

- [ ] Teste unitário: `BuscadorAdzuna.buscar(termo, dias_maximo=7)` inclui `max_days_old=7` na chamada HTTP.
- [ ] Teste unitário: `BuscadorAdzuna.buscar(termo)` (sem `dias_maximo`) não inclui `max_days_old` na chamada HTTP.
- [ ] Suíte completa dos adapters já existentes continua passando sem alteração de comportamento.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/domain/vaga_externa/buscador_vagas_externo_port.py`
- `src/infrastructure/fontes_vagas/buscador_remoteok.py`
- `src/infrastructure/fontes_vagas/buscador_wwr.py`
- `src/infrastructure/fontes_vagas/buscador_arbeitnow.py`
- `src/infrastructure/fontes_vagas/buscador_adzuna.py`
- `src/infrastructure/fontes_vagas/buscador_google_custom_search.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_adzuna.py`

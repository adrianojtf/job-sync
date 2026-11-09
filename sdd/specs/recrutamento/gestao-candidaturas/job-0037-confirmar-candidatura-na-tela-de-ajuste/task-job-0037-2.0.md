# Tarefa 2.0: Fábrica Candidatura.nova e ajuste do CriarCandidatura

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

`CriarCandidatura` monta a `Candidatura` com status `APLICADO` e o histórico inicial. O caso de uso novo (tarefa 3.0) precisa montar a mesma candidatura. Esta tarefa move essa montagem para uma fábrica no domínio, para não duplicar.

<requirements>
- Adicionar `Candidatura.nova(perfil_identificador, vaga_id, curriculo_salvo_id, empresa, cargo, agora)` como método de classe.
- A fábrica gera o `id` (UUID), define `status = APLICADO`, `data_aplicacao = agora` e `historico_status` com uma única `MudancaStatus` em `APLICADO`.
- As validações atuais de `__post_init__` continuam valendo.
- `CriarCandidatura` passa a usar a fábrica, sem mudar o resultado.
</requirements>

## Subtarefas

- [x] 2.1 Escrever os testes da fábrica (red).
- [x] 2.2 Implementar `Candidatura.nova`.
- [x] 2.3 Trocar a montagem manual em `CriarCandidatura` pela fábrica.
- [x] 2.4 Confirmar que os testes de `CriarCandidatura` e do router de candidaturas continuam passando.

## Detalhes de Implementação

Consultar em `techspec-job-0037.md` a seção "Interfaces Principais" (parágrafo "Reaproveitamento").

## Critérios de Sucesso

- A montagem da candidatura nova existe em um único lugar.
- Nenhum teste existente de `CriarCandidatura` muda de expectativa.

## Testes da Tarefa

- [x] `Candidatura.nova` devolve status `APLICADO` e data igual a `agora`.
- [x] O histórico inicial tem uma mudança em `APLICADO` com a mesma data.
- [x] Ids de duas candidaturas novas são diferentes.
- [x] Empresa ou cargo em branco levantam `ValueError`.
- [x] `CriarCandidatura` continua marcando a vaga como convertida.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/candidatura/domain/candidatura.py`
- `src/jobsync/candidatura/service_layer/criar_candidatura/service.py`
- `src/jobsync/tests/candidatura/`

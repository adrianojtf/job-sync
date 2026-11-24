# Tarefa 5.0: Limitador em memória e caso de uso `ExtrairDadosVaga`

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o limitador de leituras por usuário e o caso de uso `ExtrairDadosVaga`, que decide a fonte, a prioridade do texto e a chave de desligamento do LinkedIn.

Complexidade: medium. Dependências: 1.0, 3.0, 4.0.

<requirements>
- `LimitadorLeituraVagaEmMemoria`: janela deslizante por usuário, com limites por minuto e por dia configuráveis. Levanta `LimiteLeituraVagaExcedido` com o tempo de espera.
- `ExtrairDadosVaga.executar(entrada)`: aplica o limite, dá prioridade ao texto, normaliza o link, escolhe o leitor pela fonte, e devolve `DadosVaga`.
- Com o LinkedIn desligado, links do LinkedIn levantam `FonteVagaNaoSuportada`.
- Exige pelo menos `url` ou `texto`.
- O limite só é consumido quando há leitura de link ou chamada à IA.
</requirements>

## Subtarefas

- [ ] 5.1 Escrever os testes do limitador (minuto, dia, isolamento entre usuários, relógio injetável).
- [ ] 5.2 Implementar o limitador.
- [ ] 5.3 Criar DTOs e validador de entrada em `service_layer/extrair_dados_vaga/`.
- [ ] 5.4 Escrever os testes do caso de uso com fakes das portas.
- [ ] 5.5 Implementar `ExtrairDadosVaga`.

## Detalhes de Implementação

Ver "Interfaces Principais" da techspec. Seguir a estrutura de `service_layer/capturar_vaga/` (dtos, validator, service).

## Critérios de Sucesso

- Prioridade do texto sobre o link (critério 6 do PRD).
- LinkedIn desligado se comporta como descrito (critério 10 do PRD).

## Testes da Tarefa

- [ ] Testes de unidade: `TestLimitadorLeituraVagaEmMemoria`, `TestExtrairDadosVaga`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/prd-job-0047.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/techspec-job-0047.md`
- `src/jobsync/vaga/service_layer/capturar_vaga/`
- `src/jobsync/vaga/adapters/`
- `src/jobsync/tests/vaga/`

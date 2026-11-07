# Tarefa 4.0: Casos de uso de sugestão

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Sugestão estruturada com vaga e simplificação do caso de uso do perfil.

<requirements>
- `SugerirAjusteExperienciaAdaptada.executar(experiencia, contexto)` usando `refinar`; valida ao menos uma conquista ou contexto e o limite de tamanho; falha vira `SugestaoIAIndisponivel`.
- `SugerirAjusteExperiencia` perde `AjustadorExperienciaPort` e o parâmetro de contexto: só o melhorador sem vaga.
- Complexidade: medium. Dependências: 2.0.
</requirements>

## Subtarefas

- [ ] 4.1 Testes (Red).
- [ ] 4.2 Novo caso de uso.
- [ ] 4.3 Simplificar o existente.

## Detalhes de Implementação

Ver "Casos de uso" em `techspec-job-0035.md`.

## Critérios de Sucesso

- Sugestão chama `refinar` com o texto recebido; limite de tamanho respeitado.

## Testes da Tarefa

- [ ] Testes de unidade dos dois casos de uso.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/service_layer/sugerir_ajuste_experiencia_adaptada/`
- `src/jobsync/curriculo/service_layer/sugerir_ajuste_experiencia/`

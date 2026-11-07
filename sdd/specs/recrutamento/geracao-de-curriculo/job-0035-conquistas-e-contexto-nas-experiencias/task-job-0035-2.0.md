# Tarefa 2.0: Porta de ajuste, adapter e adaptação

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

A porta de ajuste de experiência passa a devolver `ExperienciaAdaptada` e ganha `refinar`, usado pelas sugestões da revisão.

<requirements>
- `AjustadorExperienciaPort`: `ajustar(ParaAvaliacao, ...) -> ExperienciaAdaptada` e `refinar(ExperienciaAdaptada, ...) -> ExperienciaAdaptada`.
- Prompt do adapter: de 2 a 6 conquistas com verbo de ação e resultado medido; contexto de 1 a 3 frases; preferir números da fonte e permitir estimativa conservadora; preservar cargo, empresa e período.
- Resposta em JSON `{"conquistas": [...], "contexto": "..."}`; conquistas vazias, fora de lista ou com item em branco levantam `ValueError`.
- `AdaptarCurriculoParaVaga` usa o VO e avalia o texto composto (`para_avaliacao`).
- Complexidade: high. Dependências: 1.0.
</requirements>

## Subtarefas

- [ ] 2.1 Testes do adapter e da adaptação (Red).
- [ ] 2.2 Porta.
- [ ] 2.3 Adapter e prompt.
- [ ] 2.4 Adaptação.

## Detalhes de Implementação

Ver "Prompt do adapter" em `techspec-job-0035.md`.

## Critérios de Sucesso

- O prompt contém as regras do PRD RF2 a RF6.
- Jev recebe o texto composto, e a resposta de avaliação não muda.

## Testes da Tarefa

- [ ] Testes de unidade do adapter e de `AdaptarCurriculoParaVaga`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/ajustador_experiencia_port.py`
- `src/jobsync/curriculo/adapters/ajustador_experiencia_openai_client.py`
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/`

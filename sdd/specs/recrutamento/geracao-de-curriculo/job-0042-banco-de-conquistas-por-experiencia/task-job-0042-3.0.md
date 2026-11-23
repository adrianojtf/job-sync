# Tarefa 3.0: Seleção de 3 a 5 conquistas por experiência na adaptação

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Leva as conquistas do perfil até o ajustador de experiência e faz a mesma chamada de IA escolher de 3 a 5, as mais aderentes à vaga, sem acrescentar fato.

<requirements>
- `ExperienciaParaAvaliacao.conquistas: tuple[str, ...] = ()` em `avaliacao_experiencia.py`.
- `_experiencias_do_perfil` (`curriculo_router.py`) repassa o texto das conquistas de cada experiência.
- `REGRA_SELECAO_DE_CONQUISTAS` em `prompt_contexto_vaga.py`: de 3 a 5 conquistas, as mais aderentes à vaga e ao cargo-alvo, a mais relevante primeiro; reescrita sem acrescentar fato, número, resultado, tecnologia ou prática; com menos de 3, usar todas e completar pela descrição; sem relação com a vaga, escolher as 3 mais próximas.
- O prompt de `AjustadorExperienciaOpenAIClient` inclui o bloco de conquistas cadastradas e a regra no prompt do usuário, com precedência sobre a permissão de métricas estimadas e sobre a faixa de 2 a 6 conquistas do prompt de sistema.
- Experiência com conquistas e sem descrição chama a IA; sem as duas, continua em `_sem_conteudo`.
- Sem conquistas cadastradas, o prompt fica exatamente como hoje.
- Log informativo com o número de experiências com banco e o total de conquistas, sem o texto delas.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 3.1 Escrever os testes de `_experiencias_do_perfil` (red) e do campo novo; implementar (green).
- [x] 3.2 Escrever os testes de prompt do ajustador (red): bloco de conquistas, regra de 3 a 5, proibição de número, fallback com menos de 3, regressão sem conquistas.
- [x] 3.3 Criar a constante e usar no ajustador (green).
- [x] 3.4 Escrever o teste da experiência com conquistas e sem descrição; ajustar o ramo `_sem_conteudo` (green).
- [x] 3.5 Adicionar o log em `AdaptarCurriculoParaVaga` com teste.
- [x] 3.6 Refatorar e rodar os testes de `curriculo`.

## Detalhes de Implementação

Techspec: "Pontos de Integração" (regras de prompt e conflito com a métrica estimada da JOB-0035) e "Decisões Principais" (seleção na mesma chamada). PRD: RF 7 a 14. A regra vale só para o perfil estruturado, e o PDF salvo não muda.

## Critérios de Sucesso

- O prompt pede de 3 a 5 conquistas, sem fato ou número novo, e usa a descrição como complemento.
- Perfis sem conquistas geram o mesmo prompt de antes.
- Nenhuma regressão nos testes das JOB-0035, JOB-0037 e JOB-0040.

## Testes da Tarefa

- [x] Testes de unidade em `src/jobsync/tests/curriculo/test_ajustador_experiencia_openai_client.py`.
- [x] Teste do router/helper `_experiencias_do_perfil`.
- [x] Regressão: `src/jobsync/tests/curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/avaliacao_experiencia.py`
- `src/jobsync/curriculo/adapters/ajustador_experiencia_openai_client.py`
- `src/jobsync/curriculo/adapters/prompt_contexto_vaga.py`
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/service.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/tests/curriculo/`

## Resultado da execução

- `ExperienciaParaAvaliacao.conquistas`, `REGRA_SELECAO_DE_CONQUISTAS`, bloco de conquistas no prompt do ajustador, experiência só com conquistas chama a IA, e log sem texto das conquistas.
- Testes: `src/jobsync/tests/curriculo/` e `test_routers.py` passando.

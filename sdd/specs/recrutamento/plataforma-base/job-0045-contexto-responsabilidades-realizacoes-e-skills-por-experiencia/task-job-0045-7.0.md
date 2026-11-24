# Tarefa 7.0: Ajustador de IA com os quatro blocos, serviços e API de adaptação, e currículo do perfil

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

A adaptação à vaga, as sugestões e a avaliação por experiência passam a tratar os quatro blocos, e o currículo montado do perfil usa a mesma convenção de texto.

<requirements>
- `AjustadorExperienciaOpenAIClient.ajustar` e `refinar`: uma chamada por experiência, JSON `{contexto, responsabilidades, realizacoes, skills}`; 3 a 5 itens por lista; contexto de 1 a 3 frases; a IA pode reescrever os quatro blocos para a vaga, com as regras de fidelidade das JOB-0040, JOB-0042 e JOB-0043.
- `curriculo_pre_montado.py` monta `ExperienciaParaAvaliacao` com contexto, responsabilidades, conquistas (realizações) e skills do perfil.
- Services `adaptar_curriculo_para_vaga`, `sugerir_ajuste_experiencia`, `sugerir_ajuste_experiencia_adaptada` e `avaliar_experiencia` com os quatro blocos; `Avaliar` considera os quatro blocos.
- Schemas e routers de adaptação, sugestões, avaliação e PDF revisado com os campos novos, opcionais e com padrão vazio (contrato atual não quebra).
- `MontarCurriculoDoPerfilEstruturado`: experiência estruturada em texto na convenção da task 1.0; perfil legado continua pela `descricao`.
- Perfil legado na adaptação direta segue pela `descricao`, sem os novos blocos.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 7.1 Escrever os testes do ajustador, dos services, dos routers e do montador (red).
- [x] 7.2 Implementar o prompt e o parser do ajustador (green).
- [x] 7.3 Ajustar services, DTOs, schemas e routers (green).
- [x] 7.4 Ajustar o `MontarCurriculoDoPerfilEstruturado` (green).
- [x] 7.5 Refatorar e rodar `tests/curriculo`, `tests/perfil_estruturado` e `tests/entrypoints/api`.

## Detalhes de Implementação

Techspec: "Fluxo de dados" (item 3), "Endpoints de API" e "Decisões Principais" (uma chamada de IA). PRD: RF 21 a 25 e 30.

Complexidade: high. Dependências: 2.0, 6.0.

## Critérios de Sucesso

- Adaptar um perfil com os quatro blocos devolve os quatro blocos por experiência, sem aumentar o número de chamadas de IA.
- O PDF direto e o app Streamlit continuam funcionando.
- Nenhuma regressão nos testes das JOB-0033, JOB-0034, JOB-0035 e JOB-0042.

## Testes da Tarefa

- [x] Testes do `AjustadorExperienciaOpenAIClient` (formato, limites, refino).
- [x] Testes dos services de adaptação, sugestão e avaliação.
- [x] Testes dos routers e schemas.
- [x] Testes do `MontarCurriculoDoPerfilEstruturado`.
- [x] Regressão: `src/jobsync/tests/curriculo/`, `src/jobsync/tests/perfil_estruturado/` e `src/jobsync/tests/entrypoints/api/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/ajustador_experiencia_openai_client.py`
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/{service,dtos}.py`
- `src/jobsync/curriculo/service_layer/sugerir_ajuste_experiencia_adaptada/service.py`
- `src/jobsync/curriculo/service_layer/avaliar_experiencia/`
- `src/jobsync/perfil_estruturado/domain/montar_curriculo_do_perfil_estruturado_service.py`
- `src/jobsync/entrypoints/api/curriculo_pre_montado.py`
- `src/jobsync/entrypoints/api/schemas/curriculo.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/entrypoints/streamlit_app.py`
- `src/jobsync/tests/curriculo/test_ajustador_experiencia_openai_client.py`

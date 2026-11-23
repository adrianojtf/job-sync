# Tarefa 3.0: Redator de conquista a partir do caso e endpoint de rascunho

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Transforma o caso descrito pelo candidato em uma conquista redigida, para ele revisar antes de aprovar. Nada é salvo nesta etapa.

<requirements>
- `RedatorConquistaPort.redigir(lacuna, caso, cargo, idioma_alvo) -> str` e o adapter `RedatorConquistaOpenAIClient`.
- O prompt usa só o que o candidato informou: sem número, resultado ou tecnologia que ele não citou; frase curta com verbo de ação; idioma alvo.
- Resposta fora do formato levanta `ValueError`.
- Service `RedigirConquistaDeLacuna` em `curriculo/service_layer/redigir_conquista_de_lacuna/` com `executar`; caso vazio é rejeitado.
- `POST /curriculo/lacunas/conquista-rascunho`: entrada `{tema, pergunta, caso, experiencia_indice, idioma_alvo}`; saída `{texto}`; índice inexistente devolve 404 e caso vazio, 422.
- Falha da IA devolve o erro padrão de sugestão indisponível já usado na API (ver `sugestao_ia_indisponivel.py`).
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 3.1 Escrever os testes do prompt do adapter (red) e implementar (green).
- [ ] 3.2 Escrever os testes do service (red) e implementar (green).
- [ ] 3.3 Escrever os testes do router (red): sucesso, 404, 422, IA indisponível.
- [ ] 3.4 Implementar o endpoint, os schemas e a injeção (green).
- [ ] 3.5 Refatorar e rodar os testes de `curriculo` e `entrypoints/api`.

## Detalhes de Implementação

Techspec: "Pontos de Integração" (redação) e "Endpoints de API". PRD: RF 7 a 9.

## Critérios de Sucesso

- O rascunho não contém número ou tecnologia ausentes do caso, na checagem do prompt e na avaliação manual.
- Nenhum dado é persistido neste endpoint.

## Testes da Tarefa

- [ ] Testes de unidade do adapter e do service.
- [ ] Testes do router.
- [ ] Regressão: `src/jobsync/tests/curriculo/` e `src/jobsync/tests/entrypoints/api/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/redator_conquista_port.py (novo)`
- `src/jobsync/curriculo/adapters/redator_conquista_openai_client.py (novo)`
- `src/jobsync/curriculo/service_layer/redigir_conquista_de_lacuna/ (novo)`
- `src/jobsync/curriculo/service_layer/sugestao_ia_indisponivel.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`

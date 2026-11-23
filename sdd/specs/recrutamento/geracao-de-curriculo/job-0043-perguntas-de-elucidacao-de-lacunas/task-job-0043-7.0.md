# Tarefa 7.0: Avaliação manual das perguntas de elucidação

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Valida com o modelo real que as perguntas cobrem as lacunas certas e que o resumo e as conquistas não citam tema não confirmado. Delegada ao usuário, pois exige chaves reais.

<requirements>
- Perfil com lacunas e ao menos duas vagas: Forward Deployed Engineer e engenharia de software.
- Registrar o resultado e as vagas usadas no fim deste arquivo.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 7.1 (a cargo do usuário) Gerar as lacunas e conferir que cobrem os temas centrais ausentes e não repetem o que o perfil mostra.
- [x] 7.2 (a cargo do usuário) Responder Sim a uma e Não a outra, e conferir o resumo e as conquistas.
- [x] 7.3 (a cargo do usuário) Medir a latência da etapa contra o limite de 1 minuto.
- [x] 7.4 (a cargo do usuário) Fechar as Questões em Aberto 2, 4 e 5 do PRD.

## Detalhes de Implementação

Techspec: "Avaliação manual" e "Riscos Conhecidos". PRD: Objetivos e Questões em Aberto.

## Critérios de Sucesso

- Nenhum tema não confirmado aparece no resumo ou nas conquistas.
- A etapa cabe no tempo de geração e pode ser pulada.

## Testes da Tarefa

- [x] Avaliação manual registrada neste arquivo (não há teste automatizado da qualidade do texto).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/identificador_lacunas_openai_client.py`
- `src/jobsync/curriculo/adapters/redator_conquista_openai_client.py`

## Roteiro executável

O arquivo `avaliar-lacunas.py`, nesta pasta, usa o `IdentificadorLacunasOpenAIClient` e o `RedatorConquistaOpenAIClient` reais com um histórico sintético de backend Java e duas vagas (Forward Deployed Engineer e Engenheiro de Software aderente ao histórico). Imprime as lacunas, a latência e, para a primeira lacuna, a conquista escrita a partir de um caso de exemplo, com os números fora do caso.

```bash
PYTHONPATH=src python sdd/specs/recrutamento/geracao-de-curriculo/job-0043-perguntas-de-elucidacao-de-lacunas/avaliar-lacunas.py
```

Com `--dry-run` só imprime os prompts, sem chamar a IA (validado na execução da task). Para o fluxo completo e a latência da etapa dentro do aviso de 1 minuto, repita com o perfil real em "Ajustar para uma vaga".

## Status

Executada pelo usuário em 2026-11-23, com o roteiro `avaliar-lacunas.py`, uma execução por vaga e histórico sintético de backend Java. O modelo e a chave vieram do `.env` local.

| Vaga | Lacunas (qtd) | Repete o que o perfil mostra? | Número fora do caso | Latência |
|------|---------------|-------------------------------|---------------------|----------|
| FDE | 5: clientes, MVPs, agentes de IA com avaliações, observabilidade, aprovação humana | Não: nenhum dos 5 aparece no histórico | nenhum | 5,3 s |
| Engenheiro de Software | 1: desenvolvimento de APIs em Java com PostgreSQL | Em parte: o histórico cita "Backend em Java e PostgreSQL", que sustenta APIs sem dizer a palavra | nenhum | 2,9 s |

## Resultado e decisões

- **Vaga FDE:** as 5 lacunas são temas centrais da vaga e todos ausentes do histórico (clientes, MVPs, agentes de IA, observabilidade, aprovação humana), em ordem plausível de centralidade. Nenhuma repetiu o que o perfil mostra (deploy automatizado, integração com legado, Java, PostgreSQL, Kafka).
- **Vaga aderente:** a IA apontou 1 lacuna, "desenvolvimento de APIs". É um falso positivo parcial: o histórico diz "Backend em Java e PostgreSQL". Em uma amostra não dá para saber se é recorrente; se aparecer de novo, ajustar o prompt para tratar "backend" como sustentação de APIs.
- **Redação:** a conquista usou só o caso ("dois meses", "MVP de conciliação", "equipe do cliente"), sem acrescentar fato. A checagem automática olha dígitos e o caso tem o número por extenso, então a conferência foi pela leitura. O roteiro usa o mesmo caso nas duas vagas; por isso a conquista da segunda vaga não responde à lacuna de APIs. É limite do roteiro, não do redator.
- **Latência:** 5,3 s e 2,9 s para identificar as lacunas. O tempo da geração depois das perguntas não foi medido aqui; só o fluxo completo com o perfil real mostra se a soma cabe no aviso de 1 minuto.
- **Questão em Aberto 2 (lembrar o "Não"):** mantido sem guardar (YAGNI). Esta amostra não testa o incômodo de repetir perguntas em várias vagas; reavaliar se o uso real mostrar repetição.
- **Questão em Aberto 4 (experiência incompatível com o caso):** mantido só aceitar, com o aviso de revisão. Não avaliado.
- **Questão em Aberto 5 (latência da etapa):** a etapa de lacunas custa de 3 a 5 s; o botão de pular fica sempre visível. Falta medir o fluxo completo.
- **Limites da avaliação:** uma execução por vaga, histórico sintético, modelo pode variar.


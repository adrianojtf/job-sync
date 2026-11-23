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

- [ ] 7.1 (a cargo do usuário) Gerar as lacunas e conferir que cobrem os temas centrais ausentes e não repetem o que o perfil mostra.
- [ ] 7.2 (a cargo do usuário) Responder Sim a uma e Não a outra, e conferir o resumo e as conquistas.
- [ ] 7.3 (a cargo do usuário) Medir a latência da etapa contra o limite de 1 minuto.
- [ ] 7.4 (a cargo do usuário) Fechar as Questões em Aberto 2, 4 e 5 do PRD.

## Detalhes de Implementação

Techspec: "Avaliação manual" e "Riscos Conhecidos". PRD: Objetivos e Questões em Aberto.

## Critérios de Sucesso

- Nenhum tema não confirmado aparece no resumo ou nas conquistas.
- A etapa cabe no tempo de geração e pode ser pulada.

## Testes da Tarefa

- [ ] Avaliação manual registrada neste arquivo (não há teste automatizado da qualidade do texto).

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

Não executada pela IA: o ambiente de desenvolvimento não tem `OPENAI_API_KEY`. Preencha a tabela após a execução local.

| Vaga | Lacunas (qtd) | Repete o que o perfil mostra? | Número fora do caso | Latência |
|------|---------------|-------------------------------|---------------------|----------|
| FDE | | | | |
| Engenheiro de Software | | | | |

Decisões a registrar: Questões em Aberto 2, 4 e 5 do PRD (lembrar o "Não", o aviso de experiência incompatível e a latência da etapa).


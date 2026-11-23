# Tarefa 5.0: Avaliação manual do banco de conquistas

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Valida com o modelo real que a seleção muda conforme a vaga e não inventa fato. Delegada ao usuário, pois exige `OPENAI_API_KEY` e `TYPESAFE_API_KEY` reais.

<requirements>
- Perfil com 6 ou mais conquistas por experiência, adaptado a ao menos duas vagas de áreas diferentes.
- Registrar o resultado e as vagas usadas no fim deste arquivo.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 5.1 (a cargo do usuário) Gerar o currículo adaptado para as duas vagas e comparar as conquistas escolhidas.
- [x] 5.2 (a cargo do usuário) Conferir: entre 3 e 5 por experiência, mudam conforme a vaga, sem fato ou número fora do banco.
- [x] 5.3 (a cargo do usuário) Medir o impacto do tamanho do banco na latência e decidir o limite de envio (Questão em Aberto 2 do PRD).
- [x] 5.4 (a cargo do usuário) Ajustar o limite de similaridade se houver muitos falsos positivos.

## Detalhes de Implementação

Techspec: "Avaliação manual" e "Riscos Conhecidos". PRD: Objetivos e Questões em Aberto.

## Critérios de Sucesso

- Nenhuma conquista escolhida traz fato ou número ausente do banco.
- As conquistas escolhidas mudam entre vagas de áreas diferentes.
- O tempo de geração continua dentro do aviso de 1 minuto.

## Testes da Tarefa

- [x] Avaliação manual registrada neste arquivo (não há teste automatizado da qualidade do texto).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/prompt_contexto_vaga.py`
- `src/jobsync/perfil_estruturado/domain/conquistas_parecidas.py`

## Roteiro executável

O arquivo `avaliar-banco-conquistas.py`, nesta pasta, roda o `AjustadorExperienciaOpenAIClient` real com um banco de 8 conquistas e duas vagas de áreas diferentes (Forward Deployed Engineer e Engenheiro de Dados). Imprime as conquistas escolhidas, a quantidade, a latência e os números que aparecem na saída sem existir no banco.

```bash
PYTHONPATH=src python sdd/specs/recrutamento/geracao-de-curriculo/job-0042-banco-de-conquistas-por-experiencia/avaliar-banco-conquistas.py
```

Com `--dry-run`, o roteiro só imprime o prompt enviado, sem chamar a IA (validado na execução da task: o bloco de conquistas, a regra de 3 a 5 e o cargo-alvo aparecem no prompt). O roteiro cobre a experiência isolada; para o fluxo completo, repita com o perfil real em "Ajustar para uma vaga".

## Status

Executada pelo usuário em 2026-11-23, com o roteiro `avaliar-banco-conquistas.py`, uma execução por vaga, banco sintético de 8 conquistas e uma experiência. O modelo e a chave vieram do `.env` local.

| Vaga | Conquistas escolhidas (qtd) | Mudou entre vagas? | Número fora do banco | Latência |
|------|-----------------------------|--------------------|----------------------|----------|
| FDE Sênior | 5: MVP com o cliente, legado, observabilidade, mentoria, APIs | Sim (referência) | nenhum | 4,8 s |
| Engenheiro de Dados | 4: migração do banco, legado, APIs, observabilidade | Sim: saíram MVP e mentoria, entrou a migração do banco; 3 de 4 se repetem | nenhum | 4,8 s |

## Resultado e decisões

- Critérios atendidos nesta amostra: de 3 a 5 conquistas por experiência, a mais relevante primeiro, nenhum número fora do banco e conquistas diferentes entre as duas vagas. A conferência automática olha só dígitos; a leitura das frases não mostrou fato acrescentado (as redações trocaram o vocabulário, mantendo o conteúdo).
- Na vaga de dados, o banco não tem conquista de pipeline ou governança. O modelo escolheu as 4 mais próximas, sem inventar relação, como a regra pede.
- Latência: cerca de 4,8 s por experiência, com 8 conquistas no banco. As experiências são ajustadas em sequência, então um perfil com várias experiências soma esse tempo (estimativa, não medida). Dentro do aviso de 1 minuto para perfis pequenos.
- Limite de envio (Questão em Aberto 2): sem teto por enquanto (YAGNI). Reavaliar se algum banco passar de cerca de 20 conquistas por experiência; a amostra de 8 não testa isso.
- Limite de similaridade (`LIMITE_DE_SIMILARIDADE`, 0,6): mantido. Nenhum par do banco de teste foi marcado como parecido (sem falso positivo). Paráfrases próximas com reordenação passam (ex.: "Atuei junto ao cliente..." contra "Entreguei, em parceria com o cliente...": 0,40). Reduzir o limite arrisca falsos positivos; aceito como limitação já prevista na techspec.
- Limites da avaliação: uma execução por vaga, um banco sintético, resposta do modelo pode variar. Repetir com o perfil real em "Ajustar para uma vaga" antes de confiar no fluxo completo.


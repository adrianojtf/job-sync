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

- [ ] 5.1 (a cargo do usuário) Gerar o currículo adaptado para as duas vagas e comparar as conquistas escolhidas.
- [ ] 5.2 (a cargo do usuário) Conferir: entre 3 e 5 por experiência, mudam conforme a vaga, sem fato ou número fora do banco.
- [ ] 5.3 (a cargo do usuário) Medir o impacto do tamanho do banco na latência e decidir o limite de envio (Questão em Aberto 2 do PRD).
- [ ] 5.4 (a cargo do usuário) Ajustar o limite de similaridade se houver muitos falsos positivos.

## Detalhes de Implementação

Techspec: "Avaliação manual" e "Riscos Conhecidos". PRD: Objetivos e Questões em Aberto.

## Critérios de Sucesso

- Nenhuma conquista escolhida traz fato ou número ausente do banco.
- As conquistas escolhidas mudam entre vagas de áreas diferentes.
- O tempo de geração continua dentro do aviso de 1 minuto.

## Testes da Tarefa

- [ ] Avaliação manual registrada neste arquivo (não há teste automatizado da qualidade do texto).

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

Não executada pela IA: o ambiente de desenvolvimento não tem `OPENAI_API_KEY`. Preencha a tabela abaixo após a execução local.

| Vaga | Conquistas escolhidas (qtd) | Mudou entre vagas? | Número fora do banco | Latência |
|------|-----------------------------|--------------------|----------------------|----------|
| FDE Sênior | | | | |
| Engenheiro de Dados | | | | |

Decisões a registrar: limite de conquistas enviadas por experiência (Questão em Aberto 2 do PRD) e ajuste do limite de similaridade (`LIMITE_DE_SIMILARIDADE`, hoje 0,6).


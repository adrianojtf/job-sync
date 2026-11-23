# Tarefa 7.0: E2E e fechamento

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cobre o fluxo de ponta a ponta e fecha o job. A avaliação manual com chaves reais fica a cargo do autor.

Complexidade: medium.

<requirements>
- E2E: a lista de Competências não traz o que o perfil não sustenta, e o aviso mostra a lacuna.
- Suítes completas de backend, frontend e E2E passam.
- Avaliação manual registrada como a cargo do autor, com o roteiro.
</requirements>

## Subtarefas

- [x] 7.1 Ajustar o dublê de IA do E2E ao novo contrato, se preciso.
- [x] 7.2 Escrever o E2E.
- [x] 7.3 Rodar as suítes completas.
- [x] 7.4 Registrar o roteiro da avaliação manual (vaga de agentes de IA e perfil real).

## Detalhes de Implementação

Techspec: "Design de Implementação" e "Abordagem de Testes". PRD: requisitos funcionais correspondentes.

## Critérios de Sucesso

- Os requisitos acima passam nos testes da tarefa.
- Nenhuma regressão nas JOB-0037, JOB-0040 e JOB-0041.

## Testes da Tarefa

- [x] E2E Playwright.
- [x] Regressão completa: `pytest`, `npm test` e E2E.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/e2e/fluxos.spec.ts`
- `src/jobsync/tests/e2e/app_e2e.py`

## Roteiro da avaliação manual (a cargo do autor, com chaves reais)

Em "Ajustar para uma vaga", com o perfil real e a vaga de agentes de IA que gerou a lista de cerca de 85 itens:

- [ ] Competências não traz conceito, domínio nem habilidade ("aprovação humana", "serviços financeiros" etc.).
- [ ] Competências não traz tecnologia que o perfil e as experiências não sustentem.
- [ ] A lista tem no máximo 45 itens e começa pelo que a vaga mais pede.
- [ ] As tecnologias da vaga que ficaram de fora aparecem no aviso de lacunas.
- [ ] Os itens estão agrupados nas categorias padrão (Linguagens, Backend e APIs, IA no Desenvolvimento, Qualidade e Testes, Práticas de Engenharia, Bancos de Dados, Frontend, Ferramentas).
- [ ] O resumo e as experiências não ficaram cheios de termos da vaga.
- [ ] No PDF em português a seção chama-se "Competências"; em inglês, "Skills".
- [ ] Anotar sinônimos que viraram lacuna falsa (ex.: "Postgres" e "PostgreSQL") e itens relevantes cortados pelo teto, para decidir os próximos ajustes (PRD, Questões em Aberto 2, 3 e 5).

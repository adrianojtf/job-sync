# Tarefa 13.0: Validação — suíte completa de testes + validação manual com filtro de período

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Validar a suíte completa de testes (sem regressões nas Tarefas 1.0-8.0) e, quando possível, validar manualmente o filtro de período contra fontes reais.

<requirements>
- Rodar `pytest src/tests/ -v` e confirmar 100% de sucesso, incluindo os testes novos das Tarefas 9.0-12.0.
- Validar manualmente (busca real, sem custo de IA): aplicar um filtro de 7 dias contra RemoteOK/We Work Remotely/Arbeitnow (fontes gratuitas sem cadastro) e conferir que vagas antigas (quando `data_publicacao` é parseada corretamente) somem da lista.
- Marcar as tarefas 9.0-13.0 como concluídas em `resumo-tasks-job-0007.md`.
- Complexidade: low.
</requirements>

## Subtarefas

- [ ] 13.1 Rodar a suíte completa e confirmar 100% de sucesso.
- [ ] 13.2 Validar manualmente o filtro de período com busca real (sem custo de IA — inspecionar apenas o `data_publicacao` retornado pelos buscadores antes da etapa de análise).
- [ ] 13.3 Marcar todas as tarefas como concluídas em `resumo-tasks-job-0007.md`.

## Detalhes de Implementação

Consultar a seção "Riscos Conhecidos" (filtro por período não uniformemente confiável entre fontes) de `techspec-job-0007.md` para os pontos de atenção na validação manual.

## Critérios de Sucesso

- Suíte de testes 100% verde.
- Filtro de período confirmado funcionando nas fontes que o suportam (Adzuna nativamente, demais via `data_publicacao`).

## Testes da Tarefa

- [ ] `pytest src/tests/ -v` sem falhas.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0007-descoberta-e-match-de-vagas/resumo-tasks-job-0007.md`

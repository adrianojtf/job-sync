# Tarefa 8.0: Validação manual end-to-end e execução da suíte completa de testes

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Validar manualmente o fluxo completo da Fase 3 — busca nas cinco fontes reais e candidatura em um clique — e garantir que toda a suíte de testes automatizados (Fases 0-3) continua passando.

<requirements>
- Rodar `pytest src/tests/ -v` e confirmar que todos os testes passam, incluindo os novos desta fase.
- Validar manualmente: busca com termo real retornando resultados de pelo menos duas das cinco fontes (as que não exigem cadastro: RemoteOK, We Work Remotely, Arbeitnow — Adzuna e Google Custom Search dependem de credenciais que o usuário precisa configurar).
- Validar manualmente: falha de uma fonte (ex: sem credenciais da Adzuna) não impede a exibição das demais.
- Validar manualmente: clicar em "Candidatar" gera PDF adaptado + carta de apresentação e abre a vaga original em nova aba.
- Complexidade: low.
</requirements>

## Subtarefas

- [ ] 8.1 Rodar a suíte completa de testes e confirmar 100% de sucesso.
- [ ] 8.2 Validar manualmente a busca com termo real (rodando a UI localmente).
- [ ] 8.3 Validar manualmente a resiliência a falha de fonte (fonte sem credencial configurada).
- [ ] 8.4 Validar manualmente o fluxo de "Candidatar" ponta a ponta.
- [ ] 8.5 Marcar todas as tarefas como concluídas em `resumo-tasks-job-0007.md`.

## Detalhes de Implementação

Consultar a seção "Riscos Conhecidos" de `techspec-job-0007.md` para os pontos de atenção na validação manual (cota do Google Custom Search, formato de resposta das APIs gratuitas).

## Critérios de Sucesso

- Suíte de testes 100% verde.
- Fluxo de busca + candidatura validado manualmente com pelo menos uma vaga real.

## Testes da Tarefa

- [ ] `pytest src/tests/ -v` sem falhas.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0007-descoberta-e-match-de-vagas/resumo-tasks-job-0007.md`

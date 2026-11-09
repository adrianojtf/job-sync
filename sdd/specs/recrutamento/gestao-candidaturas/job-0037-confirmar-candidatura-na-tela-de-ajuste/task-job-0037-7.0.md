# Tarefa 7.0: E2E, acessibilidade, suíte completa e lint-imports

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Fechar o JOB: validar o fluxo completo no navegador, a acessibilidade dos elementos novos e rodar toda a verificação automatizada.

<requirements>
- Teste E2E (Playwright): ajustar para uma vaga, gerar o PDF, confirmar a candidatura, ver o cartão em Aplicado no board e baixar o PDF no detalhe.
- Os dublês de IA do `app_e2e.py` continuam determinísticos.
- Teste de acessibilidade (axe) com o botão e as mensagens novas, sem violações graves.
- `pytest` completo, Vitest, typecheck do frontend e `lint-imports` verdes.
- Passo de contrato do CI sem diferença no `schema.d.ts`.
- Download do PDF no detalhe da candidatura (RF 14): o detalhe só mostrava o nome do currículo, então ganha o botão "Baixar PDF do currículo usado" (reaproveita `useBaixarCurriculo`), com testes.
- Corrigir o helper `entrar` do E2E, que seguia antes de o login terminar porque a tela de login também tem um `h1`.
- Atualizar a checklist em `resumo-tasks-job-0037.md`.
</requirements>

## Subtarefas

- [x] 7.1 Escrever o E2E do fluxo completo.
- [x] 7.2 Adicionar o botão e as mensagens ao teste de acessibilidade.
- [x] 7.3 Rodar `pytest`, Vitest, typecheck e `lint-imports`.
- [x] 7.4 Conferir o contrato (`schema.d.ts`) com Python 3.12.
- [x] 7.5 Verificar o tamanho do corpo da requisição no servidor e no Nginx com um PDF de 2 páginas (cerca de 55 KB, 74 KB em base64).
- [x] 7.7 Acrescentar o download do PDF ao detalhe da candidatura (RF 14) com testes unitários.
- [x] 7.8 Corrigir a corrida do helper `entrar` do E2E.
- [x] 7.6 Marcar as tarefas concluídas no resumo.

## Detalhes de Implementação

Consultar em `techspec-job-0037.md` as seções "Testes de Serviço" e "Riscos Conhecidos" (tamanho do corpo).

## Critérios de Sucesso

- O fluxo completo passa no E2E.
- Nenhuma violação grave de acessibilidade.
- Toda a suíte e os contratos de arquitetura verdes.
- Um PDF de 2 páginas é aceito pelo servidor e pelo Nginx.

## Testes da Tarefa

- [x] E2E do fluxo completo.
- [x] Axe com botão e mensagens novas.
- [x] `pytest` completo.
- [x] Vitest e typecheck.
- [x] `lint-imports`.
- [x] Diferença zero no `schema.d.ts`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/e2e/fluxos.spec.ts`
- `frontend/src/features/candidaturas/DetalheCandidaturaModal.tsx`
- `frontend/src/features/candidaturas/CandidaturasPage.test.tsx`
- `frontend/e2e/apoio.ts`
- `src/jobsync/tests/e2e/app_e2e.py`
- `frontend/nginx.conf.template`
- `setup.cfg`
- `sdd/specs/recrutamento/gestao-candidaturas/job-0037-confirmar-candidatura-na-tela-de-ajuste/resumo-tasks-job-0037.md`

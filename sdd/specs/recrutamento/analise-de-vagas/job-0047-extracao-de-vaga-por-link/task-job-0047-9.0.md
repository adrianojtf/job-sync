# Tarefa 9.0: Testes E2E com dublê do leitor de vagas

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cobrir os fluxos de ponta a ponta com a API real e um dublê do leitor de vagas, sem acesso à rede.

Complexidade: medium. Dependências: 8.0.

<requirements>
- Dublê do leitor em `src/jobsync/tests/e2e/app_e2e.py`: um link conhecido retorna dados fixos, outro simula falha.
- Cenário de sucesso em "Ajustar Vaga": colar link, ver campos preenchidos, editar e seguir.
- Cenário de falha: ver o motivo, colar o texto e concluir.
- Cenário de captura: confirmar o rascunho e ver a vaga salva com a origem normalizada.
- Verificação de acessibilidade (axe) nas telas alteradas, no padrão dos testes existentes.
</requirements>

## Subtarefas

- [x] 9.1 Adicionar o dublê em `app_e2e.py`.
- [x] 9.2 Escrever o E2E de Ajustar Vaga (sucesso e falha).
- [x] 9.3 Escrever o E2E da captura.
- [x] 9.4 Rodar `npm run e2e` e corrigir problemas.

## Detalhes de Implementação

Ver "Testes de Serviço" da techspec. Seguir `frontend/e2e/apoio.ts` e os specs existentes. O banco do E2E vem de `E2E_DATABASE_URL`.

## Critérios de Sucesso

- Os specs novos passam e não afetam os existentes.

## Testes da Tarefa

- [x] Testes E2E (Playwright).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/prd-job-0047.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/techspec-job-0047.md`
- `src/jobsync/tests/e2e/app_e2e.py`
- `frontend/e2e/fluxos.spec.ts`
- `frontend/e2e/apoio.ts`

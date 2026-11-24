# Tarefa 10.0: E2E e avaliação manual com o exemplo da Starian

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Valida o fluxo completo no navegador e a qualidade do conteúdo gerado pela IA, que testes automatizados não medem.

<requirements>
- Playwright: importar um currículo com blocos, editar skills, salvar, adaptar a uma vaga e arrastar uma tag entre categorias; ajustar `frontend/e2e/apoio.ts` se preciso.
- Avaliação manual com chaves reais de IA, sem teste automatizado de qualidade.
- Roteiro com o exemplo da Starian: blocos reconhecidos saem idênticos no PDF; blocos ausentes são gerados de forma realista; rótulos em pt e en.
- Registrar o tempo da importação com várias experiências (aviso atual de até 1 minuto).
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 10.1 Escrever o teste E2E do fluxo principal.
- [ ] 10.2 Rodar o E2E e corrigir os ajustes de apoio.
- [ ] 10.3 Executar o roteiro manual e registrar o resultado.
- [ ] 10.4 Registrar as questões em aberto restantes do PRD.

## Detalhes de Implementação

Techspec: "Testes de Serviço" e "Riscos Conhecidos". PRD: Objetivos e Questões em Aberto.

Complexidade: low. Dependências: 8.0, 9.0.

## Critérios de Sucesso

- O fluxo E2E passa.
- O roteiro manual confirma fidelidade do reconhecido, realismo do gerado e tempo aceitável.

## Testes da Tarefa

- [ ] Playwright em `frontend/e2e`.
- [ ] Avaliação manual com chaves reais.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/e2e/apoio.ts`
- `frontend/e2e/ (spec novo)`
- `src/jobsync/tests/e2e/app_e2e.py`

# Tarefa 3.0: Toast com ação e duração, e histórico do formulário (desfazer)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

O toast passa a aceitar um botão de ação e duração própria, e um hook guarda o instantâneo do formulário para desfazer.

<requirements>
- `notificar(mensagem, tom?, opcoes?)` com `opcoes.acao { rotulo, aoClicar }` e `opcoes.duracaoMs`; padrão de 2,6 s mantido; com ação, cerca de 6 s.
- A ação é um botão acessível e fecha o aviso ao ser usada; erros continuam em `role="alert"`.
- `use-historico-do-formulario.ts`: `registrar()` guarda `form.getValues()` e `desfazer()` restaura com `reset(valores, { keepDefaultValues: true })`, mantendo o formulário sujo.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 3.1 Escrever os testes do toast e do hook (red).
- [ ] 3.2 Implementar a ação e a duração no `ToastProvider` e no contexto (green).
- [ ] 3.3 Implementar o hook (green).
- [ ] 3.4 Refatorar e rodar `npm test`.

## Detalhes de Implementação

Techspec: "Decisões Principais" e "Visão Geral dos Componentes". PRD: RF 26 e 27.

Complexidade: low. Dependências: nenhuma.

## Critérios de Sucesso

- Os usos atuais de `notificar(mensagem, tom)` continuam iguais.
- Desfazer devolve os valores anteriores, inclusive a ordem de uma lista.

## Testes da Tarefa

- [ ] Vitest de `Toast`/`ToastProvider`.
- [ ] Vitest do `use-historico-do-formulario`.
- [ ] Regressão: `npm test`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/ui/ToastProvider.tsx`
- `frontend/src/shared/ui/toast-context.ts`
- `frontend/src/shared/ui/Toast.test.tsx`
- `frontend/src/shared/formulario-curriculo/use-historico-do-formulario.ts (novo)`
- `frontend/src/shared/formulario-curriculo/use-historico-do-formulario.test.tsx (novo)`

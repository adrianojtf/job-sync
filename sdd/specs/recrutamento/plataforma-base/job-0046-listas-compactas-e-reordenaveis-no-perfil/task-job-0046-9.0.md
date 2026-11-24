# Tarefa 9.0: E2E das listas reordenáveis e acessibilidade

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Valida no navegador a reordenação, o período inválido, os cartões lembrados, o aviso ao sair e a acessibilidade da tela.

<requirements>
- `frontend/e2e/perfil-listas.spec.ts`: arrasto real e teclado em cada lista; período inválido bloqueia o salvar; cartões abertos voltam após recarregar; aviso ao sair; limite de 15.
- Ajustar `e2e/apoio.ts` e os E2E existentes, se necessário (ex.: períodos em formato válido).
- `acessibilidade.spec.ts` (axe) sobre `/perfil` com cartões e alças.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 9.1 Escrever o E2E das listas.
- [x] 9.2 Rodar a suíte completa e corrigir os ajustes de apoio.
- [x] 9.3 Registrar o resultado e as questões que restarem.

## Detalhes de Implementação

Techspec: "Testes de Serviço" e "Riscos Conhecidos". PRD: Objetivos e Questões em Aberto.

Complexidade: medium. Dependências: 8.0.

## Critérios de Sucesso

- A suíte E2E completa passa.
- O axe não aponta violações no perfil.

## Testes da Tarefa

- [x] Playwright em `frontend/e2e`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/e2e/perfil-listas.spec.ts (novo)`
- `frontend/e2e/apoio.ts`
- `frontend/e2e/acessibilidade.spec.ts`
- `frontend/e2e/quatro-blocos.spec.ts (referência)`

# Tarefa 8.0: Integração em Meu perfil: as cinco listas, validações e aviso ao sair

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Meu perfil usa os novos modos em experiências, formação, certificações, idiomas e tecnologias, com validação de período e ano, cartão com erro aberto e aviso ao sair.

<requirements>
- Experiências, formação e certificações em modo cartão; idiomas em modo linha; tecnologias com `ListaDeTecnologias`; dados pessoais como cartão recolhível, sem reordenação.
- Resumo do cartão de experiência: primeira linha do contexto (ou da descrição) e chips com a contagem dos quatro blocos, com selo "Formato antigo".
- Período (experiência e formação) e ano (certificação) validados no campo; o cartão com erro abre sozinho; o erro 422 da API aparece com a mensagem do item.
- Limite de 15 itens nas quatro listas; "Ordenar por período" em experiências e formação, "por ano" em certificações.
- Aviso ao sair, desfazer e "Descartar" restaurando a ordem salva.
- Todas as funções atuais do cartão aberto (quatro blocos, banco de conquistas, sugestões, avaliação, estruturar perfil antigo) continuam.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 8.1 Atualizar os testes de `PerfilPage` e escrever os novos (red).
- [ ] 8.2 Ligar as listas aos novos modos e ao resumo do cartão (green).
- [ ] 8.3 Ligar as validações, os limites e as mensagens do 422 (green).
- [ ] 8.4 Ligar o aviso ao sair e o desfazer (green).
- [ ] 8.5 Refatorar e rodar `npm test`.

## Detalhes de Implementação

Techspec: "Fluxo de dados" e "Sequenciamento" (passo 8). PRD: RF 1 a 30.

Complexidade: high. Dependências: 1.0, 4.0, 5.0, 6.0, 7.0.

## Critérios de Sucesso

- Cinco experiências recolhidas cabem em uma tela de 900 px de altura.
- Período inválido bloqueia o salvar com a mensagem no campo.
- Nenhuma regressão nos testes do perfil (JOB-0042, JOB-0043, JOB-0045).

## Testes da Tarefa

- [ ] Vitest de `PerfilPage` e `formulario-perfil`.
- [ ] Regressão: `npm test`, `tsc`, ESLint e Prettier.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/perfil/PerfilPage.tsx`
- `frontend/src/features/perfil/BlocosDaExperiencia.tsx`
- `frontend/src/features/perfil/formulario-perfil.ts`
- `frontend/src/features/perfil/PerfilPage.test.tsx`
- `frontend/src/shared/formulario-curriculo/ListaItensCurriculo.tsx`

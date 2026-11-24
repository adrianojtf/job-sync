# Tarefa 5.0: Cartões abertos lembrados e modo linha única para idiomas

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

O app lembra quais cartões estavam abertos e os idiomas passam a ser linhas editáveis, sem abrir.

<requirements>
- `use-cartoes-abertos.ts`: guarda as chaves dos itens abertos em `localStorage` (`jobsync:perfil:cartoes:{perfil}:{lista}`), com `try/catch`; ao carregar vale a interseção com os itens atuais; funciona sem storage.
- A chave do item vem de `chaveDoItem` (conteúdo, não posição); item novo abre expandido.
- `modo="linha"`: alça, campos editáveis na própria linha, botões de mover e remover.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 5.1 Escrever os testes do hook e do modo linha (red).
- [x] 5.2 Implementar o hook e ligá-lo à lista (green).
- [x] 5.3 Implementar o modo linha (green).
- [x] 5.4 Refatorar e rodar `npm test`.

## Detalhes de Implementação

Techspec: "Modelos de Dados" (armazenamento local) e "Decisões Principais". PRD: RF 8 e 9.

Complexidade: medium. Dependências: 4.0.

## Critérios de Sucesso

- Recarregar a página reabre os mesmos cartões.
- Storage indisponível não quebra a tela.
- Idiomas reordenam e editam na própria linha.

## Testes da Tarefa

- [x] Vitest de `use-cartoes-abertos` (storage ausente ou com erro, item removido).
- [x] Vitest do modo linha.
- [x] Regressão: `npm test`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/use-cartoes-abertos.ts (novo)`
- `frontend/src/shared/formulario-curriculo/use-cartoes-abertos.test.ts (novo)`
- `frontend/src/shared/formulario-curriculo/ListaItensCurriculo.tsx`
- `frontend/src/shared/formulario-curriculo/CartaoDaLista.tsx`

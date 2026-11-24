# Tarefa 7.0: Aviso ao sair: hook, componente e aplicação nas telas do escopo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Pede confirmação ao sair de um formulário com alterações não salvas, por navegação, fechamento da aba ou recarga.

<requirements>
- `use-aviso-alteracoes-nao-salvas.ts` com `useBlocker` (só quando a rota muda) e `beforeunload`; `AvisoAlteracoesNaoSalvas` usa o `ConfirmacaoModal`.
- Aplicar na revisão e edição do adaptado, Ajustar vaga, Analisar ATS e Descobrir vagas; modais pequenos ficam de fora.
- Nas telas de pedido, o formulário é reiniciado após o envio com sucesso, para só avisar por texto ainda não enviado.
- Na revisão, o botão "Voltar" já confirmado não abre um segundo diálogo.
- `test/renderizar-app.tsx` e os testes de página usam um roteador de dados.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 7.1 Escrever os testes do hook e de cada tela (red).
- [ ] 7.2 Implementar o hook e o componente (green).
- [ ] 7.3 Aplicar nas quatro telas e ajustar `renderizar-app` (green).
- [ ] 7.4 Refatorar e rodar `npm test`.

## Detalhes de Implementação

Techspec: "Decisões Principais" e "Riscos Conhecidos". PRD: RF 28.

Complexidade: medium. Dependências: nenhuma.

## Critérios de Sucesso

- Navegar com alterações pendentes pede confirmação; confirmar sai, cancelar fica.
- Depois de salvar ou enviar, nada é perguntado.

## Testes da Tarefa

- [ ] Vitest do hook e das telas.
- [ ] Regressão: `npm test`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/use-aviso-alteracoes-nao-salvas.ts (novo)`
- `frontend/src/shared/formulario-curriculo/AvisoAlteracoesNaoSalvas.tsx (novo)`
- `frontend/src/features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx`
- `frontend/src/features/ajustar-vaga/AjustarVagaPage.tsx`
- `frontend/src/features/analisar-ats/AnalisarAtsPage.tsx`
- `frontend/src/features/descobrir-vagas/DescobrirVagasPage.tsx`
- `frontend/src/test/renderizar-app.tsx`

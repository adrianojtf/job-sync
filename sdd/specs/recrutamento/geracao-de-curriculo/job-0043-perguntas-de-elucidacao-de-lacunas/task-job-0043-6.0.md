# Tarefa 6.0: Frontend: etapa Perguntas sobre a vaga

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Adiciona à tela de ajuste a etapa que pergunta pelas lacunas, recolhe o caso, mostra a conquista redigida para aprovação e salva no banco, sempre com a opção de pular.

<requirements>
- Ao pedir o currículo, chamar `POST /curriculo/lacunas`; sem lacunas ou com erro, seguir direto para a geração.
- Etapa "Perguntas sobre a vaga": informa o número de perguntas; cada uma com Sim, Não e Prefiro não responder.
- Em Sim: escolher a experiência (obrigatório) e descrever o caso; chamar o rascunho; o usuário edita e aprova a conquista.
- Antes de adicionar, chamar o endpoint de parecidas da JOB-0042 e mostrar o aviso de duplicidade.
- Aprovada, chamar `POST /perfil-estruturado/experiencias/{indice}/conquistas`.
- Em Não ou Prefiro não responder, o tema não entra no currículo.
- Botão "Pular perguntas e gerar" sempre visível, inclusive durante o carregamento das lacunas.
- Sem experiências estruturadas ou com currículo de PDF salvo, a etapa não aparece.
- Acessibilidade por teclado e leitor de tela; o aviso de revisão existente continua na tela final.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 6.1 Escrever os testes do hook e do estado da etapa (red): sem lacunas, erro, pular.
- [ ] 6.2 Implementar o hook e a navegação da etapa (green).
- [ ] 6.3 Escrever os testes do fluxo Sim: experiência, caso, revisão, aprovação (red).
- [ ] 6.4 Implementar os componentes de pergunta e de revisão da conquista (green).
- [ ] 6.5 Escrever os testes do aviso de duplicidade e dos fluxos Não e Prefiro não responder; implementar.
- [ ] 6.6 Revisar acessibilidade e rodar o lint e os testes do frontend.

## Detalhes de Implementação

Techspec: "Visão Geral dos Componentes" (frontend) e "Endpoints de API". PRD: seção Experiência do Usuário e RF 5 a 12. É a task maior; se passar de uma sessão, dividir em 6.A (lacunas e perguntas) e 6.B (caso e aprovação).

## Critérios de Sucesso

- O usuário gera o currículo sem perguntas quando não há lacunas ou quando pula.
- O fluxo Sim salva uma conquista ligada à experiência escolhida.
- `npm run lint` e os testes do frontend passam.

## Testes da Tarefa

- [ ] Testes vitest de `ajustar-vaga`.
- [ ] `npm run lint` no `frontend/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/ajustar-vaga/AjustarVagaPage.tsx`
- `frontend/src/features/ajustar-vaga/use-ajustar-vaga.ts`
- `frontend/src/features/ajustar-vaga/navegacao.ts`
- `frontend/src/features/ajustar-vaga/AjustarVagaPage.test.tsx`

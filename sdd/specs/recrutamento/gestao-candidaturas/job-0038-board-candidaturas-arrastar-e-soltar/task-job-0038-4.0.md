# Tarefa 4.0: Spike do @dnd-kit: teclado, toque e ativador

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Antes de montar a UI final, validar duas dúvidas da Tech Spec: o arrasto por teclado com um botão (o título) dentro do cartão, e o arrasto por toque sem bloquear a rolagem. O resultado define se o ativador é o cartão inteiro ou uma alça de arraste.

<requirements>
- Instalar `@dnd-kit/core@6.3.1`, `@dnd-kit/sortable@10.0.0` e `@dnd-kit/utilities@3.2.2` com versões fixas e atualizar o lockfile.
- Protótipo descartável (ou teste) com `PointerSensor` (distância 6), `TouchSensor` (atraso 200 ms, tolerância 8) e `KeyboardSensor`.
- Confirmar: Espaço no cartão inicia o arrasto; Enter no título abre o detalhe sem iniciar arrasto; clique no título não vira arrasto.
- Confirmar em Chrome e, quando possível, em Safari iOS e Chrome Android que a rolagem por toque continua funcionando.
- Registrar a decisão (ativador no cartão ou alça) em uma nota no fim do `techspec-job-0038.md`.
</requirements>

## Subtarefas

- [ ] 4.1 Instalar as dependências.
- [ ] 4.2 Montar o protótipo com os três sensores.
- [ ] 4.3 Testar teclado, clique e toque, e anotar os resultados.
- [ ] 4.4 Registrar a decisão e o plano B na Tech Spec.
- [ ] 4.5 Remover o protótipo do código final.

## Detalhes de Implementação

Techspec: "Interfaces Principais" (sensores), "Riscos Conhecidos" (botão dentro de elemento arrastável; toque e rolagem).

## Critérios de Sucesso

- Decisão documentada com evidência do teste.
- Dependências instaladas e lockfile consistente, sem código de protótipo no repositório.

## Testes da Tarefa

- [ ] Teste manual registrado para teclado, clique e toque.
- [ ] `npm run build` e `npm run lint` passam com as dependências novas.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/package.json`
- `frontend/package-lock.json`
- `sdd/specs/recrutamento/gestao-candidaturas/job-0038-board-candidaturas-arrastar-e-soltar/techspec-job-0038.md`

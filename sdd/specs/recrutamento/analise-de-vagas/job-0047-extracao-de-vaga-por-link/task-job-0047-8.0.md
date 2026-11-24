# Tarefa 8.0: Frontend: campo "Link da vaga" em Ajustar Vaga e na captura

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Adicionar o campo "Link da vaga" nas telas "Ajustar currículo para vaga" e "Captura de vagas" (modal de colar vaga), com preenchimento por rascunho, revisão e alternativa de colar o texto.

Complexidade: high. Dependências: 6.0, 7.0.

<requirements>
- Componente compartilhado `CampoLinkVaga` com estados: ocioso, lendo (com cancelar), sucesso e erro.
- Hook `use-extrair-dados-vaga.ts` e método `extrairDadosVaga` em `api-client.ts` e `http-api-client.ts`.
- Em Ajustar Vaga, preencher cargo, empresa e descrição como rascunho editável, indicando os campos preenchidos e os vazios.
- Na captura, exibir o rascunho para confirmação antes de salvar, enviando URL normalizada, cargo, empresa e local.
- Em falha, mostrar o motivo (`detail`) e oferecer colar o texto, que usa o mesmo endpoint.
- Acessibilidade: operável por teclado, estados anunciados a leitores de tela.
- Regenerar `schema.d.ts` com `npm run gerar-tipos`.
</requirements>

## Subtarefas

- [ ] 8.1 Escrever os testes de `CampoLinkVaga` e do hook (MSW).
- [ ] 8.2 Implementar `CampoLinkVaga`, o hook e o cliente de API.
- [ ] 8.3 Integrar em `AjustarVagaPage.tsx`, com testes.
- [ ] 8.4 Integrar em `ColarVagaModal.tsx`, com testes.
- [ ] 8.5 Regenerar `schema.d.ts` e rodar lint, testes e build.

## Detalhes de Implementação

Ver "Componentes" e "Testes de Serviço" da techspec. Reutilizar os componentes de formulário e os padrões de mutação das features existentes.

## Critérios de Sucesso

- Fluxo de sucesso e de falha cobertos em ambas as telas.
- `npm run lint`, `npm test` e `npm run build` passam.

## Testes da Tarefa

- [ ] Testes de componente (Vitest, Testing Library e MSW).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/prd-job-0047.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/techspec-job-0047.md`
- `frontend/src/features/ajustar-vaga/AjustarVagaPage.tsx`
- `frontend/src/features/vagas-salvas/ColarVagaModal.tsx`
- `frontend/src/api/api-client.ts`
- `frontend/src/api/http-api-client.ts`
- `frontend/src/api/schema.d.ts`

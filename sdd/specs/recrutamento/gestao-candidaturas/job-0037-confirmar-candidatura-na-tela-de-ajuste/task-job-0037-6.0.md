# Tarefa 6.0: Botão "Confirmar candidatura" e estados na tela de ajuste

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Adicionar o botão ao cartão do PDF gerado, com os estados do PRD: inicial, enviando, confirmado e erro.

<requirements>
- Guardar uma cópia da vaga usada (`cargo_alvo`, `empresa_alvo`, `descricao_vaga`) quando o PDF é gerado, para o botão não depender do formulário, que pode ser editado depois.
- Mutation `confirmarCandidatura` em `use-ajustar-vaga.ts`; em sucesso, invalidar `chaveCandidaturas`, `chaveCurriculos` e `chaveVagas` do perfil.
- Botão "Confirmar candidatura" no `CurriculoGerado`, ao lado de "Baixar PDF" (que continua sendo o botão primário); só aparece com PDF gerado (RF 1).
- Empresa em branco: botão desabilitado com a explicação "Informe a empresa na vaga para confirmar a candidatura" (RF 2).
- Enviando: botão desabilitado e indicando andamento (RF 3).
- Sucesso: "Candidatura confirmada em Aplicado" com o link "Ver no board" e botão desabilitado (RF 9).
- 409: mostrar "Sua biblioteca de currículos está cheia. Remova um currículo para confirmar a candidatura." (RF 10). Outro erro: mensagem e nova tentativa (RF 11).
- Gerar um novo PDF reinicia a mutation e o botão (RF 12).
- Mensagens com `role="status"` e `role="alert"`, sem perder o foco.
- Mesmos componentes de botão e mensagem das outras telas.
</requirements>

## Subtarefas

- [ ] 6.1 Escrever os testes da tela (red).
- [ ] 6.2 Criar a mutation e a invalidação das listas.
- [ ] 6.3 Guardar a vaga do PDF gerado e passá-la ao `CurriculoGerado`.
- [ ] 6.4 Implementar o botão e os estados.
- [ ] 6.5 Reiniciar o botão ao gerar um novo PDF.

## Detalhes de Implementação

Consultar em `techspec-job-0037.md` a seção "Frontend". O ponto de captura da vaga é o `confirmarRevisao` em `AjustarVagaPage.tsx`, onde `vaga` ainda existe antes de `setVagaEmRevisao(null)`.

## Critérios de Sucesso

- O botão só aparece com PDF gerado e envia os dados da vaga que gerou aquele PDF.
- As listas de candidaturas, currículos e vagas refletem a confirmação sem recarregar a página.
- Nenhum teste existente da tela muda de expectativa.

## Testes da Tarefa

- [ ] O botão não aparece antes de o PDF ser gerado e aparece depois.
- [ ] Sem empresa, o botão fica desabilitado e mostra a explicação.
- [ ] O clique envia `cargo`, `empresa`, `descricao_vaga`, `nome_arquivo`, `pdf_base64` e o perfil.
- [ ] Sucesso mostra a mensagem e o link para o board, e desabilita o botão.
- [ ] Erro 409 mostra a mensagem de biblioteca cheia.
- [ ] Outro erro mostra a mensagem e permite tentar de novo.
- [ ] Gerar um novo PDF depois de confirmar volta o botão ao estado inicial.
- [ ] As listas de candidaturas, currículos e vagas são invalidadas.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/ajustar-vaga/AjustarVagaPage.tsx`
- `frontend/src/features/ajustar-vaga/use-ajustar-vaga.ts`
- `frontend/src/features/ajustar-vaga/AjustarVagaPage.test.tsx`
- `frontend/src/features/candidaturas/use-candidaturas.ts` (chave de cache)
- `frontend/src/features/curriculos/use-curriculos.ts` (chave de cache)
- `frontend/src/features/vagas-salvas/use-vagas-salvas.ts` (chave de cache)

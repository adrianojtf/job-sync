# Resumo de Tarefas de Implementação de Competências em Tags e Currículo Reutilizável (JOB-0041)

## Tarefas

- [x] 1.0 Domínio de competências e campo `competencias` no rascunho
- [x] 2.0 Adaptação, schemas e API do rascunho com competências
- [x] 3.0 Gerador de PDF com rótulo de categoria genérico
- [x] 4.0 Componente `EditorCompetencias` integrado à revisão
- [x] 5.0 Migração, domínio e repositório de `curriculo_adaptado`
- [ ] 6.0 Casos de uso e endpoints de `/curriculos-adaptados`
- [ ] 7.0 Vínculo com a candidatura e atualização do PDF salvo
- [ ] 8.0 Frontend: salvar ao confirmar, "Editar currículo" e modo edição
- [ ] 9.0 Reabrir o currículo depois de fechar a tela
- [ ] 10.0 Currículo adaptado como fonte de outra vaga e E2E do fluxo

## Dependências

- 1.0 não depende de nenhuma outra tarefa.
- 2.0, 3.0 e 5.0 dependem da 1.0 e podem ser feitas em paralelo.
- 4.0 depende da 2.0.
- 6.0 depende de 2.0, 3.0 e 5.0.
- 7.0 depende da 6.0.
- 8.0 depende de 4.0 e 6.0.
- 9.0 depende de 7.0 e 8.0.
- 10.0 depende de 6.0 e 8.0.
- As tarefas 1.0 a 4.0 entregam as tags sem a persistência e podem ser integradas antes das demais.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Domínio de competências e campo `competencias` no rascunho | medium | — | `revisada`, `de_texto`/`para_texto` (ida e volta) e exclusão mútua no rascunho. |
| 2.0 | Adaptação, schemas e API do rascunho com competências | medium | 1.0 | `AdaptarCurriculoParaVaga` converte a seção da IA; testes de schemas e routers. |
| 3.0 | Gerador de PDF com rótulo de categoria genérico | medium | 1.0 | Rótulo customizado em negrito, uma categoria por linha, catálogo ainda traduzido. |
| 4.0 | Componente `EditorCompetencias` integrado à revisão | high | 2.0 | Vitest: remover, criar, duplicada, categorias, acessibilidade; `formulario-revisao`. |
| 5.0 | Migração, domínio e repositório de `curriculo_adaptado` | medium | 1.0 | Agregado, fake e repositório Postgres real. |
| 6.0 | Casos de uso e endpoints de `/curriculos-adaptados` | high | 2.0, 3.0, 5.0 | Serviços, isolamento por perfil, 404/422, PDF regenerado. |
| 7.0 | Vínculo com a candidatura e atualização do PDF salvo | medium | 6.0 | Confirmação vincula; edição atualiza o PDF; falha parcial registrada em log. |
| 8.0 | Frontend: salvar ao confirmar, "Editar currículo" e modo edição | high | 4.0, 6.0 | `AjustarVagaPage` e `RevisaoCurriculoAdaptado` em modo edição. |
| 9.0 | Reabrir o currículo depois de fechar a tela | medium | 7.0, 8.0 | Páginas de Currículos e detalhe da candidatura com a ação de editar. |
| 10.0 | Currículo adaptado como fonte de outra vaga e E2E do fluxo | high | 6.0, 8.0 | Fonte `adaptado`, original intacto; Playwright do fluxo completo. |

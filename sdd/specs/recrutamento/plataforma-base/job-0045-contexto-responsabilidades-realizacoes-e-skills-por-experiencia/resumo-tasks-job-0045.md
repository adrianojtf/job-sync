# Resumo de Tarefas de Implementação de Contexto, Responsabilidades, Realizações e Skills por Experiência (JOB-0045)

## Tarefas

- [ ] 1.0 Rótulos dos quatro blocos no shared_kernel e convenção de texto do PDF
- [ ] 2.0 Domínio do perfil: quatro blocos por experiência e sincronia de skills
- [ ] 3.0 Persistência tolerante, SalvarPerfilEstruturado e contratos da API do perfil
- [ ] 4.0 Reconhecedor de blocos, porta de IA, cliente OpenAI e EstruturarExperienciaService
- [ ] 5.0 Importação de PDF com os quatro blocos e MigrarExperienciasDoPerfil com endpoint
- [ ] 6.0 ExperienciaAdaptada com os quatro blocos, rascunho e serializador na versão 2
- [ ] 7.0 Ajustador de IA com os quatro blocos, serviços e API de adaptação, e currículo do perfil
- [ ] 8.0 Frontend: perfil, importação e migração com skills em tags
- [ ] 9.0 Frontend: revisão do adaptado e EditorTags com arrastar e soltar entre categorias
- [ ] 10.0 E2E e avaliação manual com o exemplo da Starian

## Dependências

- Depende da JOB-0009, JOB-0035, JOB-0041, JOB-0042 e JOB-0043, já integradas na branch.
- 1.0 e 2.0 não dependem de outra tarefa e podem ser feitas em paralelo.
- 3.0 depende da 2.0.
- 4.0 depende da 1.0 e da 2.0.
- 5.0 depende da 3.0 e da 4.0.
- 6.0 depende da 1.0 e pode ser feita em paralelo com 3.0 a 5.0.
- 7.0 depende da 2.0 e da 6.0.
- 8.0 depende da 3.0 e da 5.0.
- 9.0 depende da 6.0 e da 7.0, e é independente da 8.0.
- 10.0 depende da 8.0 e da 9.0.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Rótulos dos quatro blocos no shared_kernel e convenção de texto do PDF | medium | nenhuma | Testes de `TestRotulosBlocosExperiencia` (pt, en, apelidos, caixa) |
| 2.0 | Domínio do perfil: quatro blocos por experiência e sincronia de skills | medium | nenhuma | Testes de `TestExperienciaProfissional` (invariantes, `eh_legada`) |
| 3.0 | Persistência tolerante, SalvarPerfilEstruturado e contratos da API do perfil | medium | 2.0 | Testes do `PerfilEstruturadoRepositoryImpl` (ida e volta e JSON antigo) |
| 4.0 | Reconhecedor de blocos, porta de IA, cliente OpenAI e EstruturarExperienciaService | high | 1.0, 2.0 | Testes de `TestReconhecedorBlocosExperiencia` (pt, en, apelidos, sem rótulo, parciais) |
| 5.0 | Importação de PDF com os quatro blocos e MigrarExperienciasDoPerfil com endpoint | medium | 3.0, 4.0 | Testes de `ImportarPerfilDePdf` (blocos reconhecidos e completados, falha da IA) |
| 6.0 | ExperienciaAdaptada com os quatro blocos, rascunho e serializador na versão 2 | medium | 1.0 | Testes de `TestExperienciaAdaptada` e `TestRascunhoCurriculoAdaptado` |
| 7.0 | Ajustador de IA com os quatro blocos, serviços e API de adaptação, e currículo do perfil | high | 2.0, 6.0 | Testes do `AjustadorExperienciaOpenAIClient` (formato, limites, refino) |
| 8.0 | Frontend: perfil, importação e migração com skills em tags | high | 3.0, 5.0 | Vitest: `formulario-perfil`, `EditorTags`, `EditorCompetencias` (regressão) e `PerfilPage` |
| 9.0 | Frontend: revisão do adaptado e EditorTags com arrastar e soltar entre categorias | high | 6.0, 7.0 | Vitest: `competencias.test.ts`, `EditorCompetencias.test.tsx`, `formulario-revisao.test.ts` e `RevisaoCurriculoAdaptado.test.tsx` |
| 10.0 | E2E e avaliação manual com o exemplo da Starian | low | 8.0, 9.0 | Playwright em `frontend/e2e` |

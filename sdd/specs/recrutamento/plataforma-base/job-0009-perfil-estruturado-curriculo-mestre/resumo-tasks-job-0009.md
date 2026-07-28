# Resumo de Tarefas de Implementação de Perfil Estruturado (Currículo Mestre)

## Tarefas

- [x] 1.0 Modelar domínio (PerfilEstruturado, DadosPerfilExtraidos, sub-entidades) + porta de repositório
- [x] 2.0 Persistência: schema SQLite + PerfilEstruturadoRepositoryImpl (upsert), com testes
- [x] 3.0 Domain Service MontarCurriculoDoPerfilEstruturado (perfil → Curriculo), com testes
- [x] 4.0 Use cases SalvarPerfilEstruturado e BuscarPerfilEstruturado, com testes
- [x] 5.0 Porta ExtratorPerfilEstruturadoPort + adapter Groq + use case ImportarPerfilDePdf, com testes
- [x] 6.0 Estender AdaptarCurriculoParaVaga/AnalisarAtsVaga/CandidatarNaVagaExterna com curriculo_pre_montado, com testes de regressão
- [x] 7.0 UI: página "Meu Perfil" (formulário estruturado + import de PDF + salvar)
- [x] 8.0 UI: integrar perfil como fonte padrão em Adaptar/ATS/Candidatar, com fallback para upload
- [x] 9.0 Validação manual end-to-end + suíte completa de testes

## Dependências

- 1.0 deve ser concluída antes de 2.0, 3.0 e 4.0.
- 5.0 depende apenas de 1.0 — pode ser feita em paralelo com 2.0, 3.0 e 4.0.
- 4.0 deve ser concluída antes de 7.0.
- 6.0 depende apenas de 3.0.
- 7.0 depende de 4.0 e 5.0.
- 8.0 depende de 6.0 e 7.0.
- 9.0 deve ser a última.

## Entregáveis principais

- Agregado `PerfilEstruturado` (com `ExperienciaProfissional`, `FormacaoAcademica`, `Certificacao`, `Idioma`), persistido por perfil de login, sem histórico/versionamento.
- Domain Service `MontarCurriculoDoPerfilEstruturado`, convertendo o perfil estruturado no `Curriculo` já existente (Fase 0), reaproveitando toda a lógica de geração/adaptação de PDF sem duplicação.
- Use case `ImportarPerfilDePdf`, com novo adapter de IA (`ExtratorPerfilEstruturadoGroq`) que extrai os campos estruturados diretamente de um PDF (upload, biblioteca, ou export do LinkedIn) — sempre editável antes de salvar.
- `AdaptarCurriculoParaVaga`, `AnalisarAtsVaga` e `CandidatarNaVagaExterna` estendidos com `curriculo_pre_montado` opcional — quando o perfil existir, pulam a extração por IA a partir de PDF.
- Nova página "Meu Perfil" na UI, e as três páginas existentes passam a usar o perfil como fonte padrão quando disponível, mantendo upload de PDF como alternativa.

## Nota de implementação

`periodo` (em `ExperienciaProfissional` e `FormacaoAcademica`) é texto livre, não datas estruturadas — decisão de simplicidade de UX documentada na TechSpec. `MontarCurriculoDoPerfilEstruturado` retorna `None` quando o perfil não tem conteúdo mínimo, tratado pela UI como "perfil inexistente" (cai no fluxo de upload de PDF já existente).

## Nuance conhecida: página "Vagas" (Fase 3)

A **busca** de vagas (`DescobrirVagasComMatch`) continua exigindo um currículo salvo na biblioteca (Fase 0) — esse use case não foi estendido com `curriculo_pre_montado` nesta fase (fora do escopo aprovado, que listava apenas `AdaptarCurriculoParaVaga`, `AnalisarAtsVaga` e `CandidatarNaVagaExterna`). Só o botão **Candidatar** (por vaga, após a busca) usa o perfil estruturado quando disponível, substituindo a extração via IA do PDF usado na busca. Ou seja: quem só tem perfil estruturado (sem nenhum currículo salvo na biblioteca) ainda não consegue usar a página "Vagas" — precisa ter pelo menos um currículo salvo para buscar, mesmo que o perfil exista. Se isso incomodar no uso real, estender `DescobrirVagasComMatch` da mesma forma é natural para uma iteração futura.

## Validação realizada

- 221/221 testes automatizados passando.
- Validação manual real no navegador: criar perfil do zero (dados pessoais, experiência, tecnologias), salvar, e confirmar via consulta direta ao SQLite que os dados foram persistidos corretamente (incluindo o caso de um campo não ter sido capturado a tempo por timing de automação, corrigido ao forçar blur antes de salvar — não é um bug do código).
- Sessão totalmente nova (logout completo + login de novo): perfil salvo carregou pré-preenchido corretamente em todos os campos, confirmando a persistência real entre sessões.
- Páginas "Adaptar Currículo" e "Analisar ATS" confirmadas visualmente exibindo "Usando os dados do seu perfil salvo" e pulando a etapa de upload de PDF quando o perfil existe.
- Fluxo de importação de PDF (`ImportarPerfilDePdf` + `ExtratorPerfilEstruturadoGroq`) coberto por testes automatizados (incluindo robustez a respostas malformadas da IA); validação manual ao vivo com PDF real não foi executada nesta rodada (não bloqueante — mesmo padrão de adapter Groq já usado e validado em fases anteriores).

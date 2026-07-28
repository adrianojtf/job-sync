# Documento de Requisitos de Produto (PRD)

## Visão Geral

Hoje, toda geração de currículo adaptado, análise de ATS ou candidatura a uma vaga descoberta depende de um upload de PDF (novo ou escolhido da biblioteca de currículos salvos, Fase 0), que é então extraído via IA (`ExtratorCurriculoSegmentadoPorIA`) para virar um `Curriculo` estruturado antes de qualquer processamento. Essa extração por IA de um PDF arbitrário está sujeita a erros de parsing, tem custo/latência, e obriga o usuário a repetir a escolha de arquivo em cada ação.

Este PRD introduz o **Perfil Estruturado** ("currículo mestre"): uma tela onde o usuário preenche diretamente os dados do seu currículo — dados pessoais, resumo profissional, experiências, formação, certificações, idiomas e tecnologias — em campos estruturados, como já faz no LinkedIn ou na Gupy. A partir do momento em que esse perfil existe, ele passa a ser a fonte principal usada por "Adaptar Currículo", "Analisar ATS" e "Candidatar" (Vagas) — sem exigir upload de PDF a cada ação. O PDF final continua sendo **gerado** a partir desses dados (reaproveitando `GeradorPdfPort`, já existente), não mais extraído de um PDF de terceiros.

A biblioteca de currículos salvos (Fase 0) não é removida: passa a servir principalmente como forma de **popular ou enriquecer** o perfil estruturado pela primeira vez (reaproveitando o extrator de IA já existente para pré-preencher os campos a partir de um PDF já existente — inclusive um export "Salvar como PDF" do próprio LinkedIn), e continua disponível como alternativa para quem prefere não preencher manualmente.

**Sobre importar do LinkedIn**: não existe API pública nem forma compatível com os Termos de Uso do LinkedIn para "puxar direto" o perfil de alguém — isso exigiria scraping, que já decidimos não fazer neste projeto (mesma regra aplicada às fontes de vaga da Fase 3). O caminho compatível é o usuário usar a função nativa "Salvar como PDF" do próprio perfil no LinkedIn e importar esse PDF pelo mecanismo de pré-preenchimento descrito acima — do ponto de vista do sistema, é só mais um PDF de entrada para o extrator de IA já existente.

## Objetivos

- Eliminar a necessidade de upload de PDF a cada geração de currículo adaptado, análise de ATS ou candidatura.
- Tornar os dados do currículo mais confiáveis, reduzindo a dependência de extração por IA de um PDF arbitrário a cada ação.
- Aproveitar dados já existentes (PDF salvo na biblioteca, ou export do LinkedIn) para pré-preencher o perfil, em vez de exigir digitação do zero.
- Sucesso é: o usuário preenche o perfil uma vez, e "Adaptar Currículo", "Analisar ATS" e "Candidatar" passam a usá-lo automaticamente, sem pedir upload de PDF.

## Histórias de Usuário

1. Como candidato, eu quero preencher meus dados de currículo em uma tela estruturada (dados pessoais, experiências, formação, tecnologias, idiomas), para não precisar fazer upload de PDF toda vez que for adaptar meu currículo para uma vaga.
2. Como candidato, eu quero poder pré-preencher esse perfil a partir de um PDF que já tenho (currículo salvo na biblioteca, ou export do meu perfil do LinkedIn), para não digitar tudo manualmente do zero.
3. Como candidato, eu quero poder editar e atualizar meu perfil a qualquer momento, para mantê-lo correto conforme minha carreira evolui.
4. Como candidato, eu quero que "Adaptar Currículo", "Analisar ATS" e "Candidatar" usem automaticamente meu perfil preenchido, sem me pedir para escolher ou subir um PDF, quando eu já tiver um perfil salvo.
5. Como candidato sem perfil ainda preenchido, eu quero continuar podendo usar essas funcionalidades fazendo upload de um PDF (comportamento atual), até decidir preencher o perfil.

## Funcionalidades Principais

### 1. Tela de Perfil (preenchimento estruturado)

- Dados pessoais: nome completo, email, LinkedIn (URL).
- Resumo profissional (equivalente à seção "Perfil" do currículo atual).
- Experiências profissionais: lista de entradas, cada uma com campos estruturados separados — empresa, cargo, período (data início/fim ou "atual") e descrição.
- Formação acadêmica: lista de entradas, cada uma com campos estruturados separados — instituição, curso e período.
- Certificações: lista de entradas (nome, instituição, ano).
- Idiomas: lista de entradas (idioma, nível).
- Tecnologias: lista de tecnologias/skills.
- Botão "Salvar perfil".

Requisitos funcionais:
1. O sistema deve permitir criar e editar um perfil estruturado com os campos acima.
2. O sistema deve persistir esse perfil vinculado ao perfil de login (`Perfil.identificador`) do usuário.
3. O sistema deve permitir múltiplas entradas de experiência, formação, certificação e idioma (adicionar e remover cada uma).
4. O sistema deve validar campos obrigatórios mínimos (nome completo, email) antes de permitir salvar.

### 2. Pré-preenchimento a partir de PDF existente

- Ao abrir a tela de perfil sem conteúdo ainda, o sistema oferece a opção de importar de um PDF (upload novo, ou escolher da biblioteca de currículos salvos), reaproveitando `ExtratorCurriculoSegmentadoPorIA` para popular os campos automaticamente.
- Os dados extraídos aparecem editáveis antes de salvar — nunca são persistidos automaticamente sem revisão do usuário.
- Esse PDF pode ser um currículo comum já salvo na biblioteca, ou um export "Salvar como PDF" do próprio LinkedIn (ver nota na Visão Geral).

Requisitos funcionais:
5. O sistema deve permitir importar dados de um PDF (upload novo ou da biblioteca existente) para pré-preencher os campos do perfil, via extração por IA já existente.
6. Os dados extraídos devem ficar editáveis antes de salvar — nunca gravados automaticamente sem revisão do usuário.

### 3. Perfil como fonte principal de geração

- Quando o perfil estruturado existir e tiver conteúdo mínimo, "Adaptar Currículo", "Analisar ATS" e "Candidatar" (na página "Vagas") usam esse perfil diretamente — sem pedir upload de PDF.
- O PDF final é **gerado** a partir do perfil (reaproveitando `GeradorPdfPort` existente), não mais extraído de um PDF de entrada.
- Se o perfil não existir ou estiver vazio, essas funcionalidades continuam funcionando com upload de PDF (comportamento atual), como alternativa.

Requisitos funcionais:
7. O sistema deve montar um `Curriculo` diretamente a partir do perfil estruturado, sem chamar o extrator de IA, quando o perfil existir e tiver conteúdo mínimo.
8. "Adaptar Currículo", "Analisar ATS" e "Candidatar" devem usar o perfil estruturado como padrão quando disponível, sem exigir upload de PDF nesse caso.
9. Essas três funcionalidades devem continuar aceitando upload de PDF como alternativa, para usuários sem perfil preenchido.

## Experiência do Usuário

Personas:
- Candidato que está usando o job-sync pela primeira vez e prefere preencher o perfil diretamente, como já faz no LinkedIn.
- Candidato que já tem um currículo em PDF (próprio ou exportado do LinkedIn) e quer aproveitá-lo para preencher o perfil mais rápido.
- Candidato que já usa o job-sync há um tempo (biblioteca de currículos da Fase 0) e quer migrar para o perfil estruturado.

Jornada principal — criação do perfil:
1. Usuário acessa a página "Meu Perfil" (novo item de menu).
2. Escolhe entre preencher do zero ou importar de um PDF (upload novo ou da biblioteca).
3. Se importar, revisa e ajusta os campos pré-preenchidos pela IA antes de salvar.
4. Salva o perfil.

Jornada principal — uso do perfil nas funcionalidades existentes:
1. Usuário acessa "Adaptar Currículo" (ou "Analisar ATS", ou "Candidatar" em "Vagas").
2. Como o perfil já existe, o sistema usa os dados dele diretamente — sem pedir upload de PDF.
3. Fluxo de adaptação/análise/candidatura segue como já existia, a partir daqui.

## Restrições Técnicas de Alto Nível

- Reaproveitar `Curriculo`/`SecaoCurriculo` (domínio) e `GeradorPdfPort`/`AjustadorTextoPort`/`GerarCartaApresentacaoPort` já existentes — não duplicar a lógica de geração/adaptação de PDF.
- Reaproveitar `ExtratorCurriculoSegmentadoPorIA` (import a partir de PDF) sem criar um segundo extrator.
- Não implementar integração direta com a API do LinkedIn (não existe acesso público para isso) nem scraping de páginas do LinkedIn — a única forma de trazer dados do LinkedIn é o usuário exportar o próprio perfil como PDF (função nativa do LinkedIn) e importar esse PDF pelo mecanismo do item "Pré-preenchimento a partir de PDF existente".

## Fora de Escopo

- Login/OAuth com LinkedIn.
- Scraping de qualquer página do LinkedIn.
- Sincronização automática ou periódica com o LinkedIn — o import é sempre uma ação manual e pontual, iniciada pelo usuário.
- Múltiplos perfis estruturados por login — um perfil por identificador nesta fase.
- Remoção da biblioteca de currículos salvos (Fase 0) — ela continua existindo, principalmente como fonte de import.

## Decisões Confirmadas

- **Experiências e formação**: campos estruturados (empresa, cargo, período, descrição / instituição, curso, período), não texto livre por entrada — mais parecido com LinkedIn/Gupy, mais fácil de validar e reordenar.
- **Biblioteca de currículos salvos (Fase 0)**: continua existindo lado a lado como está hoje (upload/salvar/remover); só deixa de ser a opção padrão em "Adaptar Currículo"/"Analisar ATS"/"Candidatar" quando o perfil estruturado já existe.
- **Edição do perfil após uso em adaptações/candidaturas passadas**: sem aviso ou versionamento nesta fase — sempre usa a versão mais atual do perfil, consistente com o restante do sistema.

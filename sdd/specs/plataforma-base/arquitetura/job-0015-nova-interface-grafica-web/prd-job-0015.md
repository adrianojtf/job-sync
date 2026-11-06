# PRD — Nova interface gráfica web do job-sync (JOB-0015)

- **Código**: `JOB-0015`
- **Módulo**: `plataforma-base`
- **Subsistema**: `arquitetura`
- **Resumo da funcionalidade**: `nova-interface-grafica-web`
- **Status**: Rascunho
- **Depende de**: [prd-job-0012.md](../job-0012-separacao-backend-frontend/prd-job-0012.md) (backend e API `/v1`)
- **Referência de design**: [carreira_saas_prototipo.html](../../../../prototipos/carreira_saas_prototipo.html) (sugestão visual, não especificação fechada)

## Visão Geral

O JOB-0012 entregou o backend do `job-sync` como uma API HTTP versionada (`/v1`). A única interface hoje é o MVP em Streamlit (`src/jobsync/entrypoints/streamlit_app.py`). Ele funciona, mas tem limites: navegação por `st.radio`, recarga da página inteira a cada interação, formulários longos sem hierarquia visual e nenhum painel que resuma a situação do candidato.

Este PRD define a nova interface web do produto, um cliente independente que consome só a API `/v1`. O protótipo em `sdd/prototipos/` define a linguagem visual: menu lateral, painel "Visão geral" com indicadores, lista de vagas recentes, card do currículo principal e um modal "Ajustar para uma vaga".

As telas não foram derivadas só do protótipo ou só do Streamlit. Elas foram validadas contra os PRDs com tasks concluídas: JOB-0004, 0005, 0006, 0007, 0009 e 0013. A tabela abaixo mostra a origem de cada tela.

| # | Tela | Origem funcional (PRD implementado) | Presente no protótipo | Presente no Streamlit |
|---|---|---|---|---|
| T1 | Entrar | JOB-0004 (login por identificador) | Não | Sim |
| T2 | Visão geral | Agregação de JOB-0004/0006/0009 | Sim | Não |
| T3 | Meu perfil (currículo mestre) | JOB-0009, JOB-0013 (avaliar experiência) | Sim (menu) | Sim |
| T4 | Meus currículos (biblioteca) | JOB-0004 | Sim (menu) | Sim (dentro de "Adaptar") |
| T5 | Ajustar para uma vaga | JOB-0005, JOB-0003, JOB-0013 | Sim (modal) | Sim |
| T6 | Analisar ATS | JOB-0005 | Não | Sim |
| T7 | Vagas salvas | JOB-0006 (captura), JOB-0013 (avaliar vaga) | Sim (menu) | Sim |
| T8 | Descobrir vagas | JOB-0007 | Não | Sim |
| T9 | Candidaturas (Kanban) | JOB-0006 | Sim (menu) | Sim |
| T10 | Configurações (token da extensão) | JOB-0006 | Sim (menu) | Sim |

**Analogia:** o backend é a cozinha, que já está pronta. O Streamlit é o balcão provisório. O protótipo é o projeto de decoração do salão. Este PRD define o cardápio, ou seja, quais pratos (telas) o salão oferece. Ele parte do que a cozinha de fato sabe preparar.

## Objetivos

1. Oferecer todas as funcionalidades já entregues no MVP Streamlit em uma interface web dedicada e mais fluida.
2. Adotar a linguagem visual do protótipo (layout, paleta, tipografia, componentes) como base do design system.
3. Dar ao candidato uma visão consolidada da sua busca em uma tela só: "Visão geral".
4. Consumir apenas a API `/v1`, sem importar código Python do domínio.
5. Manter o Streamlit funcionando durante a transição.

**Métricas de sucesso:**
- 100% das ações do Streamlit (seção "Funcionalidades Principais") estão disponíveis na nova UI.
- Fluxo principal (entrar → ajustar currículo para uma vaga → baixar PDF) em no máximo 4 cliques após colar a descrição da vaga.
- Nenhuma regra de negócio duplicada no frontend. Scores, notas e validações de domínio vêm da API.

## Histórias de Usuário

**Persona primária:** candidato(a) em busca ativa, em geral pessoa desenvolvedora. Usa o produto de forma pessoal (2 a 4 pessoas, conforme JOB-0004).

1. Como candidato, quero entrar com meu identificador e ver um resumo da minha busca, para saber o que fazer em seguida.
2. Como candidato, quero manter meu currículo mestre em campos estruturados e importar dados de um PDF, para não repetir upload a cada ação.
3. Como candidato, quero colar uma vaga e receber um currículo adaptado, a nota ATS, a carta de apresentação e as avaliações, para me candidatar com mais aderência.
4. Como candidato, quero ver as vagas que capturei pela extensão e transformá-las em candidaturas, para não perder oportunidades.
5. Como candidato, quero buscar vagas externas ordenadas por compatibilidade, para encontrar oportunidades que eu não veria sozinho.
6. Como candidato, quero mover minhas candidaturas entre etapas em um Kanban, para acompanhar o funil.
7. Como candidato, quero gerar o token da extensão de navegador, para capturar vagas enquanto navego.

**Casos extremos:**
- Perfil novo, sem currículo mestre e sem currículos salvos: a UI orienta o primeiro passo (preencher o perfil ou importar um PDF).
- Avaliação Jev indisponível (`status = indisponivel`): o fluxo segue e a UI informa que a avaliação não está disponível (JOB-0013, não bloqueante).
- Biblioteca de currículos no limite de 10 (JOB-0004): a UI informa o limite antes do upload.

## Funcionalidades Principais

### F1 — Shell da aplicação e navegação (protótipo)
- **RF1.1** Layout com menu lateral, barra superior com trilha de navegação ("Workspace / Tela atual") e área de conteúdo, conforme o protótipo.
- **RF1.2** Itens do menu: Visão geral, Meus currículos, Vagas salvas, Descobrir vagas, Candidaturas, Meu perfil e Configurações. "Ajustar para uma vaga" e "Analisar ATS" são ações acessíveis pelo botão principal e pelas telas de vaga.
- **RF1.3** O rodapé do menu mostra o identificador do perfil ativo e a ação "Sair".
- **RF1.4** Em telas estreitas, o menu lateral vira menu recolhível (comportamento responsivo do protótipo).
- **RF1.5** Toda ação assíncrona mostra estado de carregamento. O resultado aparece em toast, como no protótipo, ou em linha.

### F2 — Entrar (T1)
- **RF2.1** O usuário informa um identificador e entra. O perfil é criado se não existir (comportamento atual de `GET /v1/perfis/{id}`).
- **RF2.2** O identificador fica guardado no navegador até o usuário clicar em "Sair".

### F3 — Visão geral (T2)
- **RF3.1** Saudação com nome (do perfil estruturado, ou o identificador se não houver) e data atual.
- **RF3.2** Indicadores: currículos salvos, vagas salvas (capturadas e ainda não convertidas), candidaturas ativas (Aplicado + Entrevista) e candidaturas em Entrevista/Oferta.
- **RF3.3** Lista "Vagas recentes": últimas vagas salvas e candidaturas, com status e acesso à tela correspondente.
- **RF3.4** Card "Currículo principal": mostra o perfil estruturado e um indicador de completude. O botão "Editar currículo" leva a "Meu perfil".
- **RF3.5** Card de dica com o fluxo sugerido: importar currículo → analisar vaga → revisar → exportar.
- **RF3.6** "Atividade recente": eventos derivados das datas já existentes (captura de vaga, upload de currículo, mudanças de status de candidatura).
- **RF3.7** Botão principal "Ajustar para uma vaga" abre o fluxo F6.

### F4 — Meu perfil (T3)
- **RF4.1** Editar dados pessoais, resumo profissional, experiências, formações, certificações, idiomas (com nível) e tecnologias, com adicionar e remover itens de lista.
- **RF4.2** Importar e pré-preencher o perfil a partir de um PDF novo ou de um currículo da biblioteca, com revisão antes de salvar.
- **RF4.3** Salvar o perfil e confirmar o sucesso.
- **RF4.4** Avaliar uma experiência contra uma descrição de vaga informada, mostrando o score e as quatro dimensões (JOB-0013).

### F5 — Meus currículos (T4)
- **RF5.1** Listar os currículos salvos (nome de referência, data de upload).
- **RF5.2** Enviar um novo PDF com nome de referência, respeitando o limite de 10 por perfil.
- **RF5.3** Baixar e remover um currículo, com confirmação na remoção.

### F6 — Ajustar para uma vaga (T5)
- **RF6.1** Entrada: título da vaga, empresa e descrição (campos do modal do protótipo), mais idioma de saída (Português/Inglês) e fonte do currículo (perfil estruturado ou currículo da biblioteca).
- **RF6.2** A ação "Analisar vaga" mostra a avaliação da descrição (score geral e completude, clareza, relevância e inclusão) antes de gerar.
- **RF6.3** A ação "Gerar currículo adaptado" devolve o PDF para download e as avaliações por experiência adaptada.
- **RF6.4** Na mesma tela: nota ATS, requisitos faltantes, sugestões e a ação "Gerar carta de apresentação" com cópia e download.
- **RF6.5** Pode ser aberta já preenchida a partir de uma vaga salva (F8) ou de uma vaga descoberta (F9).

### F7 — Analisar ATS (T6)
- **RF7.1** Diagnóstico rápido sem gerar PDF: escolhe a fonte do currículo e a descrição (colada ou de uma vaga salva). Mostra a nota, os requisitos faltantes e as sugestões.

### F8 — Vagas salvas (T7)
- **RF8.1** Listar as vagas capturadas ainda não convertidas em candidatura: trecho da descrição, URL de origem e data de captura.
- **RF8.2** Registrar uma vaga colando a descrição manualmente.
- **RF8.3** Ver a descrição completa e avaliar a descrição (JOB-0013).
- **RF8.4** Criar candidatura a partir da vaga (empresa, cargo, currículo usado).
- **RF8.5** Abrir "Ajustar para uma vaga" ou "Analisar ATS" já com a descrição preenchida.

### F9 — Descobrir vagas (T8)
- **RF9.1** Buscar por termo, currículo de referência, idioma da candidatura e período de publicação (7, 15, 30 dias ou qualquer).
- **RF9.2** Listar os resultados ordenados por nota de compatibilidade, com fonte, data, requisitos faltantes e link para a vaga original.
- **RF9.3** Ação "Candidatar": gera o currículo adaptado e a carta para a vaga e abre a página original em nova aba, sem preencher formulários de terceiros (JOB-0007).

### F10 — Candidaturas (T9)
- **RF10.1** Kanban com as colunas Aplicado, Entrevista, Oferta e Rejeitado, com contagem por coluna.
- **RF10.2** Cartões com cargo, empresa e data. A mudança de etapa é feita por ação explícita (menu "Mover para"). Arrastar e soltar é opcional.
- **RF10.3** Detalhe da candidatura com o histórico de status e o currículo usado.

### F11 — Configurações (T10)
- **RF11.1** Gerar um token de captura para a extensão de navegador e exibi-lo com a ação de copiar e instruções de uso.

## Experiência do Usuário

- **Fluxo principal:** Entrar → Visão geral → "Ajustar para uma vaga" → Analisar vaga → Gerar → Baixar PDF/carta → Criar candidatura → Kanban.
- **Primeiro acesso:** a Visão geral mostra um estado vazio com a chamada "Complete seu currículo mestre" (Meu perfil ou importar PDF).
- **Design:** seguir o protótipo como guia. Fonte Inter/system-ui, cor de destaque roxa (`#635bdb`), superfícies brancas com borda sutil, cantos de 9 a 16px, toasts no canto inferior direito, modais com fechamento por `Esc` e clique fora.
- **Honestidade de produto:** notas de compatibilidade e avaliações aparecem como estimativas, com os rótulos de dimensão vindos da API (JOB-0013).
- **Acessibilidade:** navegação completa por teclado, foco visível, `aria-label` em botões só de ícone, `role="dialog"` e `aria-modal` em modais, contraste WCAG AA e textos de status além da cor.
- **Idioma da interface:** português do Brasil.

## Restrições Técnicas de Alto Nível

- O frontend consome só a API HTTP `/v1` do JOB-0012. Ele não acessa SQLite, LLMs ou fontes externas de forma direta.
- Regras de negócio (scores, notas, limites, validações de domínio) ficam no backend. O frontend apenas apresenta.
- Erros da API seguem o formato padronizado (`ProblemaResponse`) e devem aparecer como mensagens legíveis.
- Chaves de API (OpenAI, TypeSafe, Adzuna, Google) nunca chegam ao navegador.
- Deploy independente do backend.
- O MVP Streamlit continua disponível até a nova UI cobrir 100% das funcionalidades.
- Operações de IA podem levar dezenas de segundos. A UI não pode congelar e deve permitir que o usuário veja o progresso.

## Fora de Escopo

- Remoção do Streamlit (story futura, depois da validação da nova UI).
- Funcionalidades com PRD mas sem implementação: Aderência por portal (JOB-0010), Simulação de entrevista (JOB-0011) e Analytics de desempenho (JOB-0012 de `preparacao-de-carreira`). A navegação deve permitir incluí-las depois.
- Elementos do protótipo sem suporte no domínio: seletor de múltiplos workspaces, plano gratuito/pago, notificações, ajuda contextual e o indicador "Compatibilidade média" (o backend não persiste a nota por vaga).
- Editor visual do PDF gerado.
- Autenticação com senha/OAuth (o login por identificador do JOB-0004 continua valendo).
- Aplicativo mobile nativo.
- Mudanças na extensão de navegador, além de ela continuar funcionando com o token gerado na nova UI.

## Questões em Aberto

1. **Nome da marca:** o protótipo usa "carreira." e o produto se chama `job-sync`. Qual nome aparece na UI?
2. **Indicador "Compatibilidade média":** remover (decisão atual) ou criar no backend a persistência da nota ATS por vaga/candidatura?
3. **Título e empresa da vaga salva:** a entidade `Vaga` guarda só o texto e a URL. A lista de "Vagas salvas" deve mostrar um trecho do texto (decisão atual) ou o backend deve extrair título e empresa?
4. **Lacunas da API:** não há endpoint `/v1` para gerar token de captura nem para "Candidatar" em vaga externa. As duas ações existem no domínio e precisam ser expostas (detalhado na Tech Spec).
5. **Desligamento do Streamlit:** qual critério e prazo para remover o Streamlit depois da nova UI?
6. **Rastreamento de uso:** é preciso medir as métricas de sucesso (ex.: cliques no fluxo principal) ou basta validação manual?

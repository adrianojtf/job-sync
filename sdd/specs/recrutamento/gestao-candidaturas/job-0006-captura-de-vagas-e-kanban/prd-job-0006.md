# Documento de Requisitos de Produto (PRD)

## Visão Geral

Depois de adaptar um currículo para uma vaga (fluxo já existente) e ver o ATS Score (Fase 1), o usuário hoje ainda precisa controlar manualmente — em uma planilha, num bloco de notas, ou de cabeça — quais vagas já aplicou, em que fase de processo cada uma está, e qual versão de currículo/carta usou em cada uma. Este PRD introduz a entidade `Vaga` (capturada da própria página onde o usuário está navegando, sem depender de scraping automatizado ou de APIs de terceiros) e um quadro Kanban de candidaturas que conecta vaga, currículo usado e status do processo seletivo.

A captura é feita por uma extensão de navegador que extrai o texto da vaga da página atualmente aberta pelo usuário — o mesmo texto que hoje ele colaria manualmente no formulário de adaptação — evitando qualquer scraping automatizado de sites como LinkedIn ou Indeed, que violaria os termos de uso dessas plataformas.

## Objetivos

- Eliminar a necessidade de copiar/colar manualmente a descrição da vaga a cada adaptação, capturando-a diretamente da página.
- Dar visibilidade do funil de candidaturas em andamento (quantas vagas em cada estágio).
- Conectar cada candidatura ao currículo e à carta de apresentação (Fase 1) usados nela, para consulta futura.
- Sucesso é: o usuário consegue, olhando para uma tela só, responder "quantas candidaturas tenho em andamento e em que fase cada uma está".

## Histórias de Usuário

1. Como candidato, eu quero capturar o texto de uma vaga diretamente da página que estou vendo no navegador, para não precisar copiar e colar manualmente.
2. Como candidato, eu quero que a vaga capturada apareça automaticamente disponível na aplicação, pronta para eu iniciar uma adaptação de currículo a partir dela.
3. Como candidato, eu quero registrar que apliquei para uma vaga, associando a ela o currículo e a carta que usei.
4. Como candidato, eu quero mover uma candidatura entre colunas (Aplicado, Entrevista, Oferta, Rejeitado) para refletir o andamento real do processo.
5. Como candidato, eu quero ver, de forma resumida, quantas candidaturas tenho em cada estágio.

## Funcionalidades Principais

### 1. Captura de vaga via extensão de navegador

- Uma extensão de navegador (Chrome) adiciona um botão "Capturar vaga" visível enquanto o usuário navega em qualquer página.
- Ao clicar, a extensão extrai o texto principal da página (heurística simples de conteúdo, sem regras específicas por site) e envia para o perfil ativo do usuário na aplicação.
- A vaga capturada fica disponível numa lista de "vagas capturadas" dentro da aplicação principal, pronta para virar uma candidatura.

Requisitos funcionais:
1. O sistema deve prover uma extensão de navegador com um botão que capture o texto da página atual como descrição de vaga.
2. O sistema deve associar a vaga capturada ao perfil ativo do usuário (dependência: login simples da Fase 0).
3. O sistema deve registrar a URL de origem e a data de captura junto com o texto da vaga.
4. O sistema deve listar as vagas capturadas ainda não convertidas em candidatura, permitindo ao usuário revisar o texto extraído antes de prosseguir.
5. O sistema deve permitir editar manualmente o texto capturado antes de usá-lo (a extração automática pode trazer ruído da página).

### 2. Kanban de candidaturas

- Quadro com quatro colunas fixas: Aplicado, Entrevista, Oferta, Rejeitado.
- Cada candidatura é um cartão contendo: empresa, cargo, vaga associada, currículo usado, data de aplicação.
- O usuário pode mover um cartão entre colunas, e a movimentação fica registrada com data.

Requisitos funcionais:
6. O sistema deve permitir criar uma candidatura a partir de uma vaga (capturada ou colada manualmente), associando o currículo e a carta de apresentação usados.
7. O sistema deve exibir as candidaturas do perfil ativo organizadas nas quatro colunas fixas de status.
8. O sistema deve permitir mover uma candidatura de uma coluna para outra, registrando a data da mudança de status.
9. O sistema deve exibir uma contagem de candidaturas por coluna, visível no topo do quadro.
10. O sistema deve permitir abrir o detalhe de uma candidatura para rever a vaga, o currículo e a carta usados.

## Experiência do Usuário

Personas:
- Candidato ativamente aplicando para várias vagas em paralelo, que precisa de visão de funil.
- Candidato que navega em sites de vagas (LinkedIn, Gupy, empresas específicas) e quer capturar rapidamente sem sair da página.

Jornada principal:
1. Usuário está navegando numa página de vaga, clica no botão da extensão para capturar.
2. Abre a aplicação principal, vê a vaga capturada na lista, revisa o texto extraído.
3. Usuário segue para adaptação de currículo (fluxo já existente) usando essa vaga como entrada, ao invés de colar manualmente.
4. Após adaptar e decidir aplicar, cria a candidatura no Kanban, associando o currículo e a carta gerados.
5. Ao longo do processo seletivo, usuário move o cartão entre colunas conforme o andamento real.

Requisitos de UI: a extensão deve dar feedback visual imediato (ex: confirmação de "vaga capturada") sem exigir que o usuário troque de aba.

## Restrições Técnicas de Alto Nível

- A extensão de navegador não deve fazer scraping automatizado de sites de vagas — captura apenas quando o usuário clica explicitamente, e apenas o conteúdo da página que ele já está vendo.
- A comunicação entre a extensão e a aplicação principal precisa identificar o perfil ativo sem exigir novo login dentro da extensão (mecanismo de token/sessão a definir na Tech Spec).
- Deve reaproveitar a persistência (SQLite) e o modelo de perfil introduzidos na Fase 0.

## Fora de Escopo

- Scraping automatizado ou agendado de sites de vagas.
- Extensão para navegadores além de Chrome (Firefox, Safari) nesta fase.
- Colunas de Kanban customizáveis pelo usuário (fixas nas quatro definidas).
- Notificações/lembretes automáticos sobre candidaturas paradas há muito tempo em uma coluna.
- Integração com calendário para agendar entrevistas.

## Questões em Aberto

- Como a extensão deve autenticar o perfil ativo — login separado na extensão, ou algum token gerado pela aplicação principal e colado uma vez na extensão?
- Quando a extração automática do texto da página falhar ou trazer conteúdo majoritariamente irrelevante, qual deve ser o comportamento esperado (erro claro vs. captura parcial)?
- Uma candidatura pode ficar sem vaga associada (ex: aplicação feita fora do fluxo da ferramenta), ou toda candidatura exige uma vaga capturada/colada primeiro?

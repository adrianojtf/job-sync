# Documento de Requisitos de Produto (PRD)

## Visão Geral

Até aqui (Fases 0-2), o usuário sempre trouxe a vaga para o sistema — seja colando o texto manualmente, seja capturando de uma página que já estava vendo. Este PRD introduz a descoberta ativa: o sistema busca vagas em fontes externas com API pública e gratuita (RemoteOK, We Work Remotely, Arbeitnow, Adzuna), complementadas pela Google Custom Search JSON API como quinta fonte para cobrir sites não agregados pelas quatro anteriores (ex: vagas de empresas brasileiras específicas, ou portais como Gupy/Catho), e calcula um score de match entre cada vaga encontrada e o currículo salvo do usuário, usando o mesmo motor de análise de requisitos já validado nas fases anteriores. O objetivo não é substituir a busca manual em LinkedIn/Gupy, mas complementar com vagas remotas/internacionais que essas fontes agregam bem.

A Google Custom Search é a API oficial do Google (não é scraping de `google.com/search`, que violaria os Termos de Uso) — mas devolve apenas link e trecho de texto (snippet) de cada resultado, não a descrição completa da vaga como as demais fontes.

## Objetivos

- Trazer vagas relevantes até o usuário, sem que ele precise visitar múltiplos sites manualmente.
- Priorizar automaticamente as vagas mais aderentes ao perfil do usuário, usando o mesmo motor de análise de requisitos já existente.
- Reduzir o volume de vagas irrelevantes que o usuário precisa revisar manualmente.
- Sucesso é: o usuário consegue, com um clique, ver uma lista de vagas de fontes externas já ordenada por aderência ao seu currículo salvo.

## Histórias de Usuário

1. Como candidato, eu quero buscar vagas de fontes externas usando um termo de cargo, para descobrir oportunidades que eu não encontraria manualmente.
2. Como candidato, eu quero que as vagas encontradas venham ordenadas pela aderência ao meu currículo salvo, para focar primeiro nas mais relevantes.
3. Como candidato, eu quero ver por que uma vaga recebeu determinado score, olhando os requisitos que bateram e os que faltaram.
4. Como candidato, eu quero transformar uma vaga descoberta diretamente em uma candidatura no Kanban (Fase 2), sem precisar copiar/colar o texto.
5. Como candidato, eu quero ser avisado quando uma nova vaga com alta aderência aparecer, sem precisar buscar manualmente toda vez.

## Funcionalidades Principais

### 1. Busca de vagas em fontes externas

- O usuário informa um termo de busca (ex: "engenheiro de software backend") e, opcionalmente, filtros básicos (remoto/presencial, se a fonte suportar).
- O sistema consulta as fontes configuradas (RemoteOK, We Work Remotely, Arbeitnow, Adzuna, Google Custom Search) em paralelo e consolida os resultados em uma lista única.
- Para resultados vindos do Google Custom Search, o sistema busca a página do link retornado e extrai o texto principal, para chegar a uma descrição completa comparável às demais fontes (mesma heurística genérica de extração já usada na captura via extensão de navegador da Fase 2).
- Vagas duplicadas entre fontes (mesmo título + mesma empresa) são deduplicadas antes de exibir.

Requisitos funcionais:
1. O sistema deve permitir buscar vagas por termo de cargo em pelo menos as cinco fontes externas definidas (RemoteOK, We Work Remotely, Arbeitnow, Adzuna, Google Custom Search).
2. O sistema deve consolidar os resultados das diferentes fontes em uma lista única, identificando a fonte de origem de cada vaga.
3. O sistema deve deduplicar vagas idênticas (mesmo título e empresa) vindas de fontes diferentes.
4. O sistema deve tratar de forma isolada a falha de uma fonte específica (ex: Adzuna fora do ar, ou cota diária do Google Custom Search esgotada) sem impedir a exibição dos resultados das demais.
5. Para resultados do Google Custom Search, o sistema deve tentar buscar a descrição completa da página de origem; se a extração falhar, deve exibir a vaga com o snippet retornado pela busca, sinalizando que a descrição está incompleta.

### 2. Score de match com o currículo salvo

- Para cada vaga encontrada, o sistema roda a mesma análise de requisitos (`JobDescriptionAnalyzerPort`) já usada no fluxo de adaptação, e calcula um score de aderência contra um currículo salvo escolhido pelo usuário (biblioteca da Fase 0), reaproveitando a lógica de cálculo já definida no ATS Score (Fase 1).
- A lista de vagas é ordenada por score de match, do maior para o menor.
- O usuário pode ver o detalhe de por que uma vaga recebeu determinado score (requisitos batidos vs. faltantes), mesma visualização já existente no ATS Score.

Requisitos funcionais:
6. O sistema deve calcular um score de match entre cada vaga encontrada e um currículo salvo escolhido pelo usuário, reaproveitando a lógica de cálculo do ATS Score (Fase 1).
7. O sistema deve ordenar a lista de vagas encontradas por score de match, decrescente.
8. O sistema deve exibir, para cada vaga, os requisitos técnicos batidos e faltantes que compõem o score.
9. O sistema deve permitir ao usuário criar uma candidatura (Fase 2) diretamente a partir de uma vaga descoberta, pré-preenchendo a descrição da vaga no fluxo de adaptação.

## Experiência do Usuário

Personas:
- Candidato explorando o mercado sem uma vaga específica em mente, buscando por área/cargo.
- Candidato que já tem um currículo salvo (Fase 0) e quer ver rapidamente quais vagas descobertas valem a pena revisar.

Jornada principal:
1. Usuário informa um termo de busca e escolhe um currículo salvo como referência para o match.
2. Sistema consulta as fontes externas e apresenta a lista consolidada, ordenada por score.
3. Usuário revisa as vagas com maior score primeiro, abre o detalhe de requisitos batidos/faltantes.
4. Usuário escolhe uma vaga e segue direto para adaptação de currículo (fluxo já existente) ou cria uma candidatura (Fase 2).

## Restrições Técnicas de Alto Nível

- Somente fontes com API pública/gratuita — nenhuma integração deve depender de scraping de sites que proíbam automação em seus termos de uso (ex: LinkedIn, Indeed ficam fora desta fase).
- A integração com Google deve usar exclusivamente a Google Custom Search JSON API oficial, nunca scraping direto de `google.com/search` — esta última prática viola os Termos de Uso do Google.
- A Google Custom Search JSON API tem cota gratuita limitada (100 buscas/dia); o sistema deve degradar de forma graciosa (mostrar resultados das demais fontes) quando a cota for esgotada, não travar a busca inteira.
- O cálculo de match deve reaproveitar a mesma lógica de análise de requisitos já usada em `AnaliseVaga` e no ATS Score (Fase 1), sem criar um segundo motor de comparação.
- Buscas devem ter timeout individual por fonte, para que uma fonte lenta não trave a experiência inteira.

## Fora de Escopo

- Integração com LinkedIn Jobs, Indeed ou qualquer fonte que exija scraping ou viole termos de uso.
- Scraping direto de páginas de resultado do Google (`google.com/search`) — apenas a API oficial Google Custom Search é permitida.
- Alertas por e-mail ou push notification (a "notificação" nesta fase é limitada a exibição dentro da própria aplicação).
- Filtros avançados de busca (salário, senioridade estruturada) além dos que as próprias APIs externas já suportam nativamente.
- Cache ou histórico de buscas anteriores.

## Questões em Aberto

- As cinco fontes têm formatos de resposta e campos diferentes (nem todas trazem salário, nível de senioridade) — qual o conjunto mínimo de campos que toda vaga consolidada precisa ter para entrar na lista?
- Deduplicação por "mesmo título + mesma empresa" pode ter falsos positivos (empresas com nomes ligeiramente diferentes entre fontes) — vale a pena um critério mais tolerante, ou começamos estrito e ajustamos depois?
- "Alertar quando uma vaga de alta aderência aparecer" (história de usuário 5) depende de busca recorrente automática — isso deve rodar em background nesta fase, ou fica para uma iteração futura, mantendo a busca apenas sob demanda por enquanto?
- A cota gratuita do Google Custom Search (100 buscas/dia) é compartilhada entre todos os perfis do sistema (mesma chave de API) — isso é aceitável no contexto de uso pessoal/2-4 pessoas, ou cada busca deve consumir a cota de forma consciente (ex: avisar o usuário quantas buscas restam no dia)?
- Como o Google Custom Search exige configurar um "mecanismo de busca programável" (Programmable Search Engine) restrito a sites específicos ou aberto à web toda — a busca deve ser restrita a uma lista curada de sites de vagas, ou aberta a qualquer resultado?

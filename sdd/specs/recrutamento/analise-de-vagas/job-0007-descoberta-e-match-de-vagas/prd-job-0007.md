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
4. Como candidato, eu quero clicar em "Candidatar" numa vaga descoberta e já receber meu currículo adaptado para ela, com a análise de ATS feita, sem precisar repetir manualmente o fluxo de adaptação.
5. Como candidato, eu quero decidir quando buscar vagas — clicando em um botão — em vez de o sistema rodar buscas sozinho em segundo plano sem eu pedir.

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

### 3. Candidatura em um clique

- A funcionalidade tem um item próprio no menu lateral, chamado "Vagas" (separado de "Adaptar Currículo", "Analisar ATS" e "Vagas & Candidaturas" do Kanban da Fase 2).
- Cada vaga da lista tem um botão "Candidatar". Ao clicar, o sistema roda em sequência: análise de ATS + adaptação completa do currículo (mesma lógica de `AdaptarCurriculoParaVaga`, Fase 0) + geração da carta de apresentação (Fase 1) para aquela vaga específica.
- Ao final, o sistema abre a URL original da vaga (`VagaExterna.url`) em nova aba, para o usuário aplicar manualmente no site de origem, e disponibiliza o PDF do currículo adaptado e o texto da carta para download/cópia.
- Não há preenchimento automático (autofill) de formulários em sites de terceiros: cada site de vaga tem uma estrutura de formulário diferente, e automatizar isso de forma genérica seria frágil e exigiria manutenção site a site. A automação se limita a preparar os artefatos (PDF + carta) e abrir a vaga original — o preenchimento do formulário de candidatura em si continua manual.

Requisitos funcionais:
9. O sistema deve oferecer um botão "Candidatar" em cada vaga descoberta, que executa em um único clique: análise de ATS, adaptação do currículo e geração da carta de apresentação para aquela vaga.
10. Ao candidatar, o sistema deve abrir a URL original da vaga em nova aba e disponibilizar o PDF adaptado e a carta de apresentação para download.
11. O sistema não deve tentar preencher automaticamente formulários de candidatura em sites de terceiros — a automação termina na preparação dos artefatos e abertura da vaga original.

### 4. Filtro por período de publicação

- O usuário pode restringir a busca a vagas publicadas nos últimos 7, 15 ou 30 dias, ou não aplicar filtro nenhum ("qualquer período").
- Cada fonte expõe a data de publicação de forma diferente: **Adzuna** aceita um parâmetro nativo (`max_days_old`) que filtra no próprio servidor da API; **RemoteOK**, **We Work Remotely** e **Arbeitnow** não têm parâmetro de busca por data, mas cada resposta traz um campo de data por vaga, usado para filtrar depois de buscar (client-side); **Google Custom Search** não informa quando a vaga foi publicada (só quando o Google indexou a página, que é uma coisa diferente) — por isso resultados dessa fonte sempre entram como "data desconhecida", sem tentar aproximar com a data de indexação, para não passar uma falsa sensação de precisão.
- Vagas cuja data de publicação não pôde ser determinada com confiança (sempre o caso do Google Custom Search) continuam aparecendo no resultado filtrado, sinalizadas como "data de publicação desconhecida" — a decisão do produto é não esconder vagas potencialmente relevantes só por falta de metadado confiável.

Requisitos funcionais:
12. O sistema deve permitir filtrar as vagas buscadas por período de publicação: últimos 7, 15 ou 30 dias, ou sem filtro (qualquer período).
13. Quando uma fonte suportar filtro de data nativamente (Adzuna), o sistema deve usá-lo na própria chamada à API.
14. Para fontes sem filtro nativo confiável, o sistema deve filtrar localmente com base na data de publicação retornada por vaga, quando disponível.
15. Vagas sem data de publicação determinável devem ser exibidas mesmo com o filtro de período ativo, sinalizadas visualmente como data desconhecida — nunca ocultadas silenciosamente.

## Experiência do Usuário

Personas:
- Candidato explorando o mercado sem uma vaga específica em mente, buscando por área/cargo.
- Candidato que já tem um currículo salvo (Fase 0) e quer ver rapidamente quais vagas descobertas valem a pena revisar.

Jornada principal:
1. Usuário informa um termo de busca e escolhe um currículo salvo como referência para o match.
2. Sistema consulta as fontes externas e apresenta a lista consolidada, ordenada por score.
3. Usuário revisa as vagas com maior score primeiro, abre o detalhe de requisitos batidos/faltantes.
4. Usuário clica em "Candidatar" na vaga escolhida: o sistema roda a análise de ATS, adapta o currículo e gera a carta de apresentação para aquela vaga, abre a vaga original em nova aba e disponibiliza o PDF adaptado + carta para download.

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
- Filtros avançados de busca (salário, senioridade estruturada) além dos que as próprias APIs externas já suportam nativamente e do filtro por período de publicação (7/15/30 dias) descrito acima.
- Cache ou histórico de buscas anteriores.
- Preenchimento automático (autofill) de formulários de candidatura em sites de terceiros — cada site tem uma estrutura própria, e automatizar isso de forma genérica seria frágil; o botão "Candidatar" prepara os artefatos (PDF + carta) e abre a vaga original, mas o preenchimento do formulário continua manual.
- Busca automática/recorrente em background (scheduler, cron job, ou qualquer execução periódica sem o usuário pedir). A busca é **sempre** iniciada por uma ação explícita do usuário (clique no botão "Buscar vagas") — nunca disparada sozinha pelo sistema. Isso inclui o alerta de "vaga de alta aderência" mencionado originalmente na história de usuário 5: decidido que não haverá busca automática nesta fase nem em iterações futuras próximas, para evitar consumo não controlado de cota de API (Groq, Google Custom Search) sem uma ação consciente do usuário — ver risco de esgotamento de cota descoberto durante a validação da Tarefa 8.0 na TechSpec.

## Questões em Aberto

- As cinco fontes têm formatos de resposta e campos diferentes (nem todas trazem salário, nível de senioridade) — qual o conjunto mínimo de campos que toda vaga consolidada precisa ter para entrar na lista?
- Deduplicação por "mesmo título + mesma empresa" pode ter falsos positivos (empresas com nomes ligeiramente diferentes entre fontes) — vale a pena um critério mais tolerante, ou começamos estrito e ajustamos depois?
- A cota gratuita do Google Custom Search (100 buscas/dia) é compartilhada entre todos os perfis do sistema (mesma chave de API) — isso é aceitável no contexto de uso pessoal/2-4 pessoas, ou cada busca deve consumir a cota de forma consciente (ex: avisar o usuário quantas buscas restam no dia)?
- Como o Google Custom Search exige configurar um "mecanismo de busca programável" (Programmable Search Engine) restrito a sites específicos ou aberto à web toda — a busca deve ser restrita a uma lista curada de sites de vagas, ou aberta a qualquer resultado?

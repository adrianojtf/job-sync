# Documento de Requisitos de Produto (PRD)

## Visão Geral

Hoje o "Analisar ATS" (Fase 1, `job-0005`) calcula um único score genérico de aderência: compara os requisitos técnicos explícitos extraídos da descrição da vaga contra o conteúdo do currículo, sem distinguir para qual portal/ATS aquela vaga será submetida. Na prática, o mesmo currículo pode passar na triagem de um portal e ser mal ranqueado ou rejeitado em outro, porque cada plataforma (Gupy, LinkedIn, Greenhouse, Workday, etc.) tem critérios de triagem e parsing diferentes.

Este PRD introduz a **Aderência por Portal**: em vez de um único score genérico, o usuário escolhe (ou o sistema detecta automaticamente pela URL da vaga) o portal de destino, e o sistema calcula um score ponderado específico para aquele portal — reaproveitando o motor de análise de requisitos já existente (Fase 1) como um dos fatores, e adicionando novos fatores mensuráveis (como a estrutura do PDF). O usuário também pode comparar a aderência do mesmo currículo contra vários portais ao mesmo tempo.

**Ressalva central de honestidade de produto**: ninguém fora da Gupy, LinkedIn, Greenhouse etc. conhece os pesos reais dos algoritmos proprietários de cada portal. Os "perfis de portal" deste módulo são **estimativas heurísticas do job-sync**, baseadas em boas práticas de mercado publicamente conhecidas — não uma engenharia reversa do algoritmo real. Isso precisa ficar explícito na UI (nunca comunicar o score como "isto é o que a Gupy vai calcular", e sim "estimativa de aderência baseada em boas práticas conhecidas para este portal"), para não prometer uma precisão que não temos como sustentar.

## Objetivos

- Dar ao candidato uma visão de aderência específica por portal, em vez de um único score genérico que não reflete diferenças reais entre plataformas.
- Eliminar parte da incerteza de "por que passei num portal e não em outro", sem prometer replicar algoritmos proprietários que não temos acesso.
- Permitir comparar a aderência do mesmo currículo contra múltiplos portais em um único fluxo.
- Sucesso é: o usuário escolhe (ou tem detectado automaticamente) o portal de uma vaga e recebe um score + gaps + recomendações específicos daquele perfil de portal, deixando claro que é uma estimativa.

## Histórias de Usuário

1. Como candidato, eu quero que o sistema detecte automaticamente o portal de uma vaga pela URL (quando capturada pela extensão ou descoberta na Fase 3), para não precisar informar isso manualmente toda vez.
2. Como candidato, eu quero poder selecionar manualmente o portal de destino quando a detecção automática não for possível (vaga colada manualmente, ou portal fora do catálogo), para ainda assim ter uma análise direcionada.
3. Como candidato, eu quero ver o score decomposto por fator (ex: aderência de palavras-chave, estrutura do documento), para entender o que pesa mais naquele portal.
4. Como candidato, eu quero comparar a aderência do mesmo currículo contra vários portais ao mesmo tempo, para decidir onde focar meus ajustes.
5. Como candidato, eu quero deixar claro para mim mesmo que esses scores são estimativas do job-sync, não uma garantia do que cada portal realmente vai calcular, para calibrar minhas expectativas.

## Funcionalidades Principais

### 1. Catálogo de perfis de portal (MVP restrito)

- Um conjunto inicial de perfis de portal com pesos definidos, cobrindo apenas os portais para os quais existe informação pública específica o suficiente para montar um perfil com algum fundamento (não um chute genérico): **Gupy**, **LinkedIn**, **Greenhouse**, **Workday**.
- Cada perfil de portal define os fatores que pesam no score e o peso de cada um, usando apenas fatores que o job-sync consegue de fato medir (ver Restrições Técnicas).
- Novos portais podem ser adicionados depois, mas exigem a mesma pesquisa de base — não é uma lista arbitrariamente expansível sem fundamento.

Requisitos funcionais:
1. O sistema deve manter um catálogo de perfis de portal (Gupy, LinkedIn, Greenhouse, Workday nesta fase), cada um com fatores e pesos próprios.
2. Cada perfil de portal deve deixar explícito, na interface, que os pesos são uma estimativa heurística do job-sync, não o algoritmo real do portal.

### 2. Detecção automática de portal por URL

- Ao analisar uma vaga que já tenha uma URL de origem associada (capturada pela extensão, Fase 2, ou descoberta na busca externa, Fase 3), o sistema tenta identificar o portal por padrões de domínio/URL (ex: `gupy.io`, `linkedin.com`, `myworkdayjobs.com`, `greenhouse.io`).
- Se a URL não corresponder a nenhum portal do catálogo, ou não houver URL (vaga colada manualmente), o sistema cai para seleção manual.

Requisitos funcionais:
3. O sistema deve detectar automaticamente o portal de uma vaga a partir da URL de origem, quando disponível, usando padrões de domínio conhecidos do catálogo.
4. Quando a detecção automática não identificar um portal do catálogo, o sistema deve permitir a seleção manual entre os portais do catálogo, ou um perfil "genérico" (ver Funcionalidade 4).

### 3. Score de aderência ponderado por portal

- Reaproveita o motor de análise de requisitos já existente (`JobDescriptionAnalyzerPort` + `CalcularAtsScore`, Fase 1) como o fator "aderência de palavras-chave" em todos os perfis de portal.
- Adiciona um segundo fator mensurável: estrutura do documento (currículos gerados pelo próprio job-sync, via perfil estruturado da Fase 5 ou adaptação da Fase 0, são sempre de coluna única e texto simples — estrutura considerada adequada por construção; currículos de PDF enviados pelo usuário podem ter estrutura menos previsível).
- O score final por portal é a soma ponderada dos fatores mensuráveis daquele perfil, normalizada de 0 a 100.
- Exibe o detalhamento por fator (não só o número final), replicando o formato já usado no "Analisar ATS" (Fase 1).

Requisitos funcionais:
5. O sistema deve calcular um score de 0 a 100 por portal, combinando os fatores mensuráveis daquele perfil de portal de forma ponderada.
6. O sistema deve exibir o detalhamento do score por fator (nome do fator, peso, nota parcial), não apenas o número final.
7. O sistema deve continuar exibindo os requisitos técnicos batidos/faltantes (já existente na Fase 1) como parte do detalhamento do fator de palavras-chave.

### 4. Perfil "Genérico"

- Quando o portal não é identificado nem selecionado manualmente, ou o usuário simplesmente não quer especificar um portal, o sistema oferece um perfil "Genérico" — equivalente ao comportamento atual do "Analisar ATS" (Fase 1), sem ponderação por portal.

Requisitos funcionais:
8. O sistema deve sempre oferecer um perfil "Genérico" como alternativa, preservando o comportamento do "Analisar ATS" já existente para quem não quer (ou não pode) especificar um portal.

### 5. Comparativo entre portais

- O usuário pode rodar a análise do mesmo currículo contra todos os portais do catálogo de uma vez, vendo os scores lado a lado.

Requisitos funcionais:
9. O sistema deve permitir comparar o score do mesmo currículo (para a mesma vaga) contra todos os perfis de portal do catálogo em uma única ação, exibindo os resultados lado a lado.

## Experiência do Usuário

Personas:
- Candidato que captura uma vaga pela extensão (Fase 2) ou descobre uma vaga externa (Fase 3) e quer saber a aderência específica para aquele portal antes de se candidatar.
- Candidato que cola manualmente a descrição de uma vaga sem uma URL identificável, e escolhe manualmente o portal de destino.

Jornada principal:
1. Usuário acessa "Analisar ATS" com uma vaga que já tem URL de origem (capturada ou descoberta).
2. Sistema detecta o portal automaticamente (ex: Gupy) e exibe isso para o usuário, com opção de trocar manualmente.
3. Usuário roda a análise; vê o score geral do perfil daquele portal, o detalhamento por fator, e os requisitos faltantes.
4. Usuário opcionalmente clica em "Comparar com outros portais" e vê o mesmo currículo pontuado contra Gupy/LinkedIn/Greenhouse/Workday lado a lado.
5. Usuário ajusta o currículo com base nas recomendações e repete a análise.

## Restrições Técnicas de Alto Nível

- Reaproveitar integralmente `JobDescriptionAnalyzerPort`, `CalcularAtsScore` (Domain Service, Fase 1) e `GerarSugestoesAtsPort` — a ponderação por portal é uma camada nova sobre esse motor já existente, não um segundo motor de análise.
- Os perfis de portal (pesos e fatores) só podem incluir fatores que o job-sync consegue efetivamente medir com os dados que já possui (texto da vaga, conteúdo do currículo, estrutura do PDF quando aplicável). Fatores que dependeriam de acessar a plataforma real do portal (formulários, perguntas eliminatórias, completude de campos preenchidos na plataforma, endosses do LinkedIn) ficam fora desta fase — não há como medir isso sem integração direta com o portal, que não existe.
- Nenhuma integração direta ou scraping de páginas de portal (Gupy, LinkedIn, Greenhouse, Workday) para obter esses dados — mesma regra já aplicada à Fase 3 (fontes de vaga) e à Fase 5 (perfil estruturado).
- A detecção de portal por URL deve reaproveitar as URLs já capturadas por `Vaga.url_origem` (Fase 2) e `VagaExterna.url` (Fase 3), sem introduzir uma nova forma de captura de URL.

## Fora de Escopo

- Réplica ou engenharia reversa dos algoritmos reais de Gupy (Gaia), LinkedIn, Greenhouse ou Workday — os perfis desta fase são estimativas heurísticas de boas práticas públicas, não os algoritmos reais.
- Fatores que exigem acesso à plataforma do portal em si: completude de campos preenchidos na plataforma, respostas de knockout questions, contagem de endorsements do LinkedIn, fit cultural/DISC (mencionados no documento de referência, mas não mensuráveis pelo job-sync sem integração direta).
- Catálogo amplo de portais (o documento de referência lista 10 portais BR + 10 globais) — esta fase cobre só os quatro com informação pública específica suficiente (Gupy, LinkedIn, Greenhouse, Workday); expandir o catálogo é uma iteração futura, sujeita à mesma exigência de fundamento.
- Exportação em .docx (mencionada como preferência do Workday no documento de referência) — pode ser uma fase futura independente, não faz parte desta.
- Detecção de portal via análise semântica/LLM para portais fora do catálogo de padrões de URL conhecidos — nesta fase, fora do catálogo cai direto para seleção manual ou perfil genérico.
- Qualquer promessa de métrica de conversão real (ex: "aumento de X% na taxa de avanço para entrevista") — não temos como validar isso sem dados de resultado real de candidaturas em volume, e mesmo o rastreamento de status do Kanban (Fase 2) desta base de usuários é pequeno demais para sustentar uma métrica assim.

## Questões em Aberto

- Os pesos exatos de cada fator, por perfil de portal (ex: quanto keyword match pesa vs. estrutura do documento no perfil Gupy) — precisam ser definidos e documentados na TechSpec, com a devida ressalva de que são uma estimativa nossa.
- A "estrutura do documento" deve ser sempre nota 100 para currículos gerados pelo próprio job-sync (perfil estruturado ou adaptação), e uma heurística real (via `pdfplumber`, checando múltiplas colunas/imagens) só para PDFs enviados pelo usuário (biblioteca) — confirmar se vale o esforço de implementar a heurística real nesta fase, ou se um valor fixo/estimado é suficiente para o MVP.
- Onde esta funcionalidade entra na navegação: substitui a página "Analisar ATS" (Fase 1) adicionando a seleção de portal a ela, ou vira uma página nova separada? A recomendação é evoluir "Analisar ATS" em vez de duplicar uma página nova, mas isso deve ser confirmado antes da TechSpec.

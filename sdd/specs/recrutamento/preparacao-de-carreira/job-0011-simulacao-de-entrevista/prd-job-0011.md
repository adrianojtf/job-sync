# Documento de Requisitos de Produto (PRD)

> Nota: este PRD nasceu de uma divisão do antigo `job-0008` (que cobria Simulação de Entrevista e Analytics juntos). Este documento cobre exclusivamente a Simulação de Entrevista; a parte de Analytics virou `job-0012`.

## Visão Geral

Com o Kanban de candidaturas (Fase 2) já registrando o funil completo — vaga, currículo usado, status e histórico de mudanças — o sistema tem dados suficientes para ajudar o usuário a se preparar para a entrevista de uma candidatura específica. Este PRD cobre a geração de um roteiro de perguntas prováveis de entrevista, via IA, a partir da vaga real e do currículo usado naquela candidatura.

## Objetivos

- Ajudar o usuário a chegar mais preparado para entrevistas, com perguntas relevantes à vaga específica, não genéricas.
- Sucesso é: o usuário consegue gerar um roteiro de perguntas prováveis para uma candidatura específica, direto da tela onde já acompanha o status dela.

## Histórias de Usuário

1. Como candidato com uma entrevista marcada, eu quero gerar uma lista de perguntas prováveis baseadas na vaga real, para chegar mais preparado.
2. Como candidato, eu quero que as perguntas geradas considerem tanto os requisitos técnicos da vaga quanto o meu currículo, para identificar pontos que provavelmente serão questionados.

## Funcionalidades Principais

### 1. Simulação de entrevista com IA

- A partir de uma candidatura existente no Kanban (Fase 2), o usuário pode gerar um roteiro de perguntas prováveis, usando a `AnaliseVaga` já associada àquela candidatura e o currículo usado nela.
- As perguntas são organizadas por tema (técnicas, comportamentais, específicas da vaga), sem repetir perguntas genéricas de entrevista que não tenham relação com a vaga.
- O usuário pode gerar um novo roteiro quantas vezes quiser para a mesma candidatura (não há limite).

Requisitos funcionais:
1. O sistema deve gerar um roteiro de perguntas prováveis de entrevista a partir de uma candidatura existente, usando a análise de vaga e o currículo já associados a ela.
2. O sistema deve organizar as perguntas geradas em pelo menos duas categorias (ex: técnicas e comportamentais).
3. O sistema deve permitir gerar um novo roteiro para a mesma candidatura sob demanda, sem limite de repetição.
4. O sistema deve exibir o roteiro gerado na tela de detalhe da candidatura (já existente na Fase 2).

## Experiência do Usuário

Personas:
- Candidato que acabou de ser chamado para entrevista e quer se preparar rapidamente.

Jornada principal:
1. Usuário abre o detalhe de uma candidatura no Kanban (já em status "Entrevista", por exemplo).
2. Clica em "Gerar roteiro de entrevista", vê as perguntas organizadas por categoria.
3. Pode gerar novamente se quiser variações.

## Restrições Técnicas de Alto Nível

- A geração de perguntas deve reaproveitar a mesma integração com a API Groq já usada nas fases anteriores, sem novo provedor de IA.

## Fora de Escopo

- Ver "Roadmap Futuro" abaixo — entrevista simulada interativa fica fora desta fase.

## Roadmap Futuro (fora desta fase)

- **Entrevista simulada interativa**: em vez de só gerar o roteiro de perguntas, conduzir uma simulação completa de pergunta-resposta, com a IA avaliando as respostas do usuário em tempo real (ex: dando feedback sobre completude, clareza, aderência à vaga). Destacado explicitamente pelo usuário como candidato a uma próxima versão, não descartado — mas depende de decisões de UX ainda não exploradas (texto ou voz? avaliação em que critérios? quantas rodadas?), por isso fica fora desta fase, que entrega apenas o roteiro estático de perguntas.

## Questões em Aberto

- O roteiro de perguntas deve incluir sugestões de resposta baseadas no currículo do usuário, ou apenas as perguntas (deixando a resposta inteiramente com o usuário)?

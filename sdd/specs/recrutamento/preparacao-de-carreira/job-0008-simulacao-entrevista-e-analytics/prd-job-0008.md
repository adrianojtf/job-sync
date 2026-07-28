# Documento de Requisitos de Produto (PRD)

## Visão Geral

Com o Kanban de candidaturas (Fase 2) já registrando o funil completo — vaga, currículo usado, status e histórico de mudanças — o sistema tem dados suficientes para fechar o ciclo do produto: ajudar o usuário a se preparar para a entrevista de uma candidatura específica, e mostrar, de forma agregada, o que está funcionando no processo de busca (quais currículos/idiomas/fontes geram mais avanço no funil). Este PRD cobre duas funcionalidades que dependem diretamente do histórico acumulado nas fases anteriores: simulação de entrevista com IA baseada na vaga real, e um dashboard pessoal de analytics.

## Objetivos

- Ajudar o usuário a chegar mais preparado para entrevistas, com perguntas relevantes à vaga específica, não genéricas.
- Dar visibilidade sobre quais versões de currículo, idiomas ou fontes de vaga estão de fato avançando no funil, para o usuário ajustar sua estratégia.
- Fechar o ciclo do produto: da adaptação de currículo até o aprendizado sobre o que funciona.
- Sucesso é: o usuário consegue gerar um roteiro de perguntas prováveis para uma candidatura específica, e visualizar, em um só painel, sua taxa de avanço por versão de currículo.

## Histórias de Usuário

1. Como candidato com uma entrevista marcada, eu quero gerar uma lista de perguntas prováveis baseadas na vaga real, para chegar mais preparado.
2. Como candidato, eu quero que as perguntas geradas considerem tanto os requisitos técnicos da vaga quanto o meu currículo, para identificar pontos que provavelmente serão questionados.
3. Como candidato, eu quero ver quantas candidaturas avançaram (de Aplicado para Entrevista, de Entrevista para Oferta) nos últimos meses, para entender minha taxa de sucesso.
4. Como candidato, eu quero comparar a taxa de avanço entre diferentes versões de currículo que usei, para saber qual está performando melhor.
5. Como candidato, eu quero ver a distribuição de candidaturas por status atual (quantas em cada coluna do Kanban), como visão rápida do funil.

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

### 2. Dashboard de analytics pessoal

- Painel com métricas agregadas calculadas a partir do histórico de candidaturas do Kanban: contagem por status atual, taxa de avanço (% de candidaturas que saíram de "Aplicado" para qualquer estágio seguinte), e taxa de avanço segmentada por currículo salvo usado.
- Os dados são sempre do perfil ativo — sem comparação entre perfis diferentes.

Requisitos funcionais:
5. O sistema deve exibir a contagem atual de candidaturas por status (Aplicado, Entrevista, Oferta, Rejeitado).
6. O sistema deve calcular e exibir a taxa de avanço geral (% de candidaturas que saíram do status inicial "Aplicado").
7. O sistema deve calcular e exibir a taxa de avanço segmentada por currículo salvo usado, permitindo comparar performance entre versões.
8. O dashboard deve refletir apenas dados do perfil ativo no momento.

## Experiência do Usuário

Personas:
- Candidato que acabou de ser chamado para entrevista e quer se preparar rapidamente.
- Candidato que já acumulou várias candidaturas ao longo do tempo e quer entender padrões no próprio processo.

Jornada principal — simulação de entrevista:
1. Usuário abre o detalhe de uma candidatura no Kanban (já em status "Entrevista", por exemplo).
2. Clica em "Gerar roteiro de entrevista", vê as perguntas organizadas por categoria.
3. Pode gerar novamente se quiser variações.

Jornada principal — analytics:
1. Usuário acessa uma nova aba/seção "Meu desempenho" dentro da aplicação.
2. Vê contagem por status, taxa de avanço geral, e taxa de avanço por currículo usado.

## Restrições Técnicas de Alto Nível

- A geração de perguntas deve reaproveitar a mesma integração com a API Groq já usada nas fases anteriores, sem novo provedor de IA.
- O dashboard depende inteiramente dos dados já persistidos pelo Kanban (Fase 2) — não introduz nova coleta de dados, apenas agregação do que já existe.
- Cálculos de analytics devem ser recalculados sob demanda (ao abrir o dashboard), sem exigir um job agendado nesta fase.

## Fora de Escopo

- Comparação de desempenho entre usuários/perfis diferentes.
- Exportação do dashboard em PDF ou outro formato.
- Métricas de tempo médio em cada estágio do funil (ex: dias até avançar de Aplicado para Entrevista) — fica para uma iteração futura.

## Roadmap Futuro (fora desta Fase 4)

- **Entrevista simulada interativa**: em vez de só gerar o roteiro de perguntas, conduzir uma simulação completa de pergunta-resposta, com a IA avaliando as respostas do usuário em tempo real (ex: dando feedback sobre completude, clareza, aderência à vaga). Destacado explicitamente pelo usuário como candidato a uma próxima versão, não descartado — mas depende de decisões de UX ainda não exploradas (texto ou voz? avaliação em que critérios? quantas rodadas?), por isso fica fora desta Fase 4, que entrega apenas o roteiro estático de perguntas.

## Questões em Aberto

- O roteiro de perguntas deve incluir sugestões de resposta baseadas no currículo do usuário, ou apenas as perguntas (deixando a resposta inteiramente com o usuário)?
- Qual o volume mínimo de candidaturas necessário para a "taxa de avanço por currículo" fazer sentido estatisticamente (ex: esconder a métrica se houver menos de 3 candidaturas com aquele currículo)?
- O dashboard deve considerar algum período (ex: últimos 90 dias) ou sempre o histórico completo do perfil?

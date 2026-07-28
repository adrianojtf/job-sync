# Documento de Requisitos de Produto (PRD)

> Nota: este PRD nasceu de uma divisão do antigo `job-0008` (que cobria Simulação de Entrevista e Analytics juntos). Este documento cobre exclusivamente o Analytics de Desempenho; a parte de Simulação de Entrevista virou `job-0011`.

## Visão Geral

Com o Kanban de candidaturas (Fase 2) já registrando o funil completo — vaga, currículo usado, status e histórico de mudanças — o sistema tem dados suficientes para mostrar, de forma agregada, o que está funcionando no processo de busca do usuário (quais versões de currículo geram mais avanço no funil). Este PRD cobre um dashboard pessoal de analytics ("Meu Desempenho"), fechando o ciclo do produto: da adaptação de currículo até o aprendizado sobre o que funciona.

## Objetivos

- Dar visibilidade sobre quais versões de currículo estão de fato avançando no funil, para o usuário ajustar sua estratégia.
- Sucesso é: o usuário visualiza, em um só painel, sua taxa de avanço geral e por versão de currículo.

## Histórias de Usuário

1. Como candidato, eu quero ver quantas candidaturas avançaram (de Aplicado para Entrevista, de Entrevista para Oferta) nos últimos meses, para entender minha taxa de sucesso.
2. Como candidato, eu quero comparar a taxa de avanço entre diferentes versões de currículo que usei, para saber qual está performando melhor.
3. Como candidato, eu quero ver a distribuição de candidaturas por status atual (quantas em cada coluna do Kanban), como visão rápida do funil.

## Funcionalidades Principais

### 1. Dashboard de analytics pessoal

- Painel com métricas agregadas calculadas a partir do histórico de candidaturas do Kanban: contagem por status atual, taxa de avanço (% de candidaturas que saíram de "Aplicado" para qualquer estágio seguinte), e taxa de avanço segmentada por currículo salvo usado.
- Os dados são sempre do perfil ativo — sem comparação entre perfis diferentes.

Requisitos funcionais:
1. O sistema deve exibir a contagem atual de candidaturas por status (Aplicado, Entrevista, Oferta, Rejeitado).
2. O sistema deve calcular e exibir a taxa de avanço geral (% de candidaturas que saíram do status inicial "Aplicado").
3. O sistema deve calcular e exibir a taxa de avanço segmentada por currículo salvo usado, permitindo comparar performance entre versões.
4. O dashboard deve refletir apenas dados do perfil ativo no momento.

## Experiência do Usuário

Personas:
- Candidato que já acumulou várias candidaturas ao longo do tempo e quer entender padrões no próprio processo.

Jornada principal:
1. Usuário acessa uma nova aba/seção "Meu desempenho" dentro da aplicação.
2. Vê contagem por status, taxa de avanço geral, e taxa de avanço por currículo usado.

## Restrições Técnicas de Alto Nível

- O dashboard depende inteiramente dos dados já persistidos pelo Kanban (Fase 2) — não introduz nova coleta de dados, apenas agregação do que já existe.
- Cálculos de analytics devem ser recalculados sob demanda (ao abrir o dashboard), sem exigir um job agendado nesta fase.

## Fora de Escopo

- Comparação de desempenho entre usuários/perfis diferentes.
- Exportação do dashboard em PDF ou outro formato.
- Métricas de tempo médio em cada estágio do funil (ex: dias até avançar de Aplicado para Entrevista) — fica para uma iteração futura.

## Questões em Aberto

- Qual o volume mínimo de candidaturas necessário para a "taxa de avanço por currículo" fazer sentido estatisticamente (ex: esconder a métrica se houver menos de 3 candidaturas com aquele currículo)?
- O dashboard deve considerar algum período (ex: últimos 90 dias) ou sempre o histórico completo do perfil?

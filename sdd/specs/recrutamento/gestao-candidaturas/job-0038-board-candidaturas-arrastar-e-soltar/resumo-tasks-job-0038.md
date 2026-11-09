# Resumo de Tarefas de Implementação do Board de Candidaturas com Arrastar e Soltar (JOB-0038)

## Tarefas

- [x] 1.0 Domínio e persistência da ordem dos cartões
- [x] 2.0 Caso de uso MoverCandidatura com posição e endpoint de submissão
- [ ] 3.0 Contrato e cliente de API no frontend
- [ ] 4.0 Spike do @dnd-kit: teclado, toque e ativador
- [ ] 5.0 Lógica do board no frontend e atualização otimista
- [ ] 6.0 Componentes do board e interações
- [ ] 7.0 Layout responsivo e visual estilo Jira
- [ ] 8.0 E2E, acessibilidade e fechamento

## Dependências

- 1.0 e 4.0 não dependem de nenhuma outra tarefa e podem ser feitas em paralelo.
- 1.0 deve ser concluída antes de 2.0.
- 2.0 deve ser concluída antes de 3.0 (o cliente usa o contrato OpenAPI regenerado).
- 3.0 deve ser concluída antes de 5.0.
- 4.0 e 5.0 devem ser concluídas antes de 6.0.
- 6.0 deve ser concluída antes de 7.0.
- 1.0 a 7.0 devem ser concluídas antes de 8.0.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Domínio e persistência da ordem dos cartões | high | — | `reposicionar` em todos os casos de borda; `aplicar_movimento` transacional; migração de banco antigo |
| 2.0 | Caso de uso MoverCandidatura com posição e endpoint de submissão | medium | 1.0 | Posição omitida, limitada ao fim e inexistente; compatibilidade do endpoint |
| 3.0 | Contrato e cliente de API no frontend | low | 2.0 | Corpo da requisição com e sem `posicao` |
| 4.0 | Spike do @dnd-kit: teclado, toque e ativador | medium | — | Teclado com botão interno; clique x arrasto; toque sem travar a rolagem |
| 5.0 | Lógica do board no frontend e atualização otimista | medium | 3.0 | Casos de borda do destino; restauração do cache em erro; serialização de movimentos |
| 6.0 | Componentes do board e interações | high | 4.0, 5.0 | Teclado; título x arrasto; erro com restauração; "Mover para" no modal |
| 7.0 | Layout responsivo e visual estilo Jira | medium | 6.0 | Conferência visual em 375, 768 e 1280 px |
| 8.0 | E2E, acessibilidade e fechamento | medium | 1.0 a 7.0 | Arrasto real por ponteiro; persistência; larguras; toque; axe |

## Entregáveis principais

- Candidaturas movidas por arrastar e soltar (mouse, toque e teclado), entre colunas e dentro da coluna.
- Ordem dos cartões salva por coluna e preservada ao recarregar, com migração dos dados existentes.
- Detalhe aberto pelo clique no título; botão "Detalhes" e `select` do cartão removidos.
- Campo "Mover para" no modal de detalhe, como alternativa ao arrasto.
- Board responsivo com colunas de largura fixa, rolagem horizontal e visual no estilo de boards de mercado.
- Endpoint de submissão compatível com o contrato atual (campo `posicao` opcional).

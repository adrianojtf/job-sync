# Resumo de Tarefas de Implementação de Conquistas e Contexto nas Experiências (JOB-0035)

## Tarefas

- [x] 1.0 ExperienciaAdaptada e refatoração do rascunho
- [x] 2.0 Porta de ajuste, adapter e adaptação
- [x] 3.0 Gerador de PDF e prompt da fonte PDF
- [x] 4.0 Casos de uso de sugestão
- [x] 5.0 API
- [ ] 6.0 Cliente de API e tipos
- [ ] 7.0 SugestaoIA genérico e formulário
- [ ] 8.0 Tela de revisão
- [ ] 9.0 E2E, acessibilidade e suíte completa

## Dependências

- Backend: 1.0 → 2.0 e 3.0 (em paralelo) → 4.0 → 5.0.
- Frontend: 6.0 (depende de 5.0) → 7.0 → 8.0 → 9.0.

## Decisões adotadas

- Contratos: a task 5.0 só soma os campos novos (`conquistas`, `contexto` e o endpoint `/experiencias-adaptadas/sugestoes`). Os legados (`descricao` e `contexto_vaga`) saem na task 8.0, depois que o frontend migrar, para o frontend, os tipos gerados e o E2E ficarem verdes a cada task.
- Faixa de conquistas: de 2 a 6 no prompt; o domínio exige ao menos uma.
- `contexto_vaga` removido de `/experiencias-profissionais/sugestoes`.
- Fonte PDF incluída por convenção de texto (task 3.0).
- Métricas estimáveis pela IA, com aviso fixo na revisão (decisão de produto).
- Regenerar o `schema.d.ts` com Python 3.12, o mesmo do CI.

# Resumo de Tarefas de Implementação das Sugestões de IA por Seção (JOB-0034)

## Tarefas

- [x] 1.0 ContextoVaga e AnaliseVagaSchema
- [x] 2.0 Porta MelhoradorTextoCurriculoPort e adapter OpenAI
- [ ] 3.0 Casos de uso SugerirAjusteSecaoCurriculo e SugerirAjusteExperiencia
- [ ] 4.0 Endpoints de sugestão e análise da vaga no rascunho
- [ ] 5.0 Cliente de API e tipos do frontend
- [ ] 6.0 Componente SugestaoIA
- [ ] 7.0 Integração das sugestões na revisão
- [ ] 8.0 Integração das sugestões em Meu perfil
- [ ] 9.0 E2E, acessibilidade e suíte completa

## Dependências

- Backend: 1.0 e 2.0 em paralelo, depois 3.0 → 4.0.
- Frontend: 5.0 (depende de 4.0) → 6.0 → 7.0 e 8.0 (em paralelo) → 9.0.

## Decisões adotadas

- Tecnologias no modo vaga: reaproveita `AjustadorTextoPort` como está; o usuário vê a sugestão antes de aplicar (risco aberto no PRD, questão 2).
- Limite de 5.000 caracteres por texto (valor proposto, não medido).

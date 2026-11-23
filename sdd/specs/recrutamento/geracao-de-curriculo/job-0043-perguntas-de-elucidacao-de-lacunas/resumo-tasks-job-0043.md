# Resumo de Tarefas de Implementação de Perguntas de Elucidação de Lacunas (JOB-0043)

## Tarefas

- [ ] 1.0 Domínio de lacunas, porta, adapter de IA e caso de uso IdentificarLacunasDaVaga
- [ ] 2.0 Endpoint POST /curriculo/lacunas
- [ ] 3.0 Redator de conquista a partir do caso e endpoint de rascunho
- [ ] 4.0 Comando AdicionarConquistaAExperiencia e endpoint
- [ ] 5.0 Resumo usando as conquistas do histórico
- [ ] 6.0 Frontend: etapa Perguntas sobre a vaga
- [ ] 7.0 Avaliação manual das perguntas de elucidação

## Dependências

- Depende da JOB-0042 (banco de conquistas e endpoint de parecidas) e da JOB-0040 (regra do resumo), já documentadas.
- 1.0 não depende de outra tarefa desta JOB, mas só começa depois da JOB-0042.
- 2.0 e 3.0 dependem da 1.0 e podem ser feitas em paralelo.
- 4.0 depende só da JOB-0042 e pode ser feita em paralelo com 1.0 a 3.0.
- 5.0 depende da JOB-0040 e da JOB-0042.
- 6.0 depende da 2.0, da 3.0 e da 4.0.
- 7.0 depende da 5.0 e da 6.0.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Domínio de lacunas, porta, adapter de IA e caso de uso IdentificarLacunasDaVaga | medium | JOB-0042 | `LacunaDaVaga` e `principais`; `IdentificarLacunasDaVaga` (limite de 5, falha vira vazio, sem experiências não chama a IA); prompt do adapter. |
| 2.0 | Endpoint POST /curriculo/lacunas | low | 1.0 | Router: devolve as lacunas do perfil do usuário; lista vazia com perfil sem experiências ou com falha da IA; 422 sem vaga. |
| 3.0 | Redator de conquista a partir do caso e endpoint de rascunho | medium | 1.0 | Prompt do redator (sem acrescentar fato, número ou tecnologia); service; endpoint de rascunho com 404 e 422. |
| 4.0 | Comando AdicionarConquistaAExperiencia e endpoint | medium | JOB-0042 | `com_conquista_na_experiencia` (índice, origem, duplicata); `AdicionarConquistaAExperiencia`; endpoint com 404 e 422. |
| 5.0 | Resumo usando as conquistas do histórico | low | JOB-0040, JOB-0042 | `ContextoVaga` com o campo novo; prompt do Perfil com as conquistas; sem conquistas o prompt não muda; router preenche o campo. |
| 6.0 | Frontend: etapa Perguntas sobre a vaga | high | 2.0, 3.0, 4.0 | Vitest em `ajustar-vaga`: sem lacunas a etapa não aparece; fluxo Sim, experiência, caso, revisão e aprovação; Não, Prefiro não responder e Pular. |
| 7.0 | Avaliação manual das perguntas de elucidação | low | 5.0, 6.0 | Avaliação manual com chaves reais, sem teste automatizado de qualidade. |

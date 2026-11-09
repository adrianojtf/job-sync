# Resumo de Tarefas de Implementação de Aderência das Experiências e do Resumo à Vaga (JOB-0037)

## Tarefas

- [x] 1.0 Cargo-alvo no ContextoVaga e portas com ContextoVaga
- [x] 2.0 Equivalências e plano de adaptação no domínio
- [ ] 3.0 Identificador de equivalências (porta e adapter)
- [ ] 4.0 Trocas, cargo-alvo e responsabilidades implícitas na adaptação
- [ ] 5.0 Refino variável no backend
- [ ] 6.0 API, Postman e tipos do frontend
- [ ] 7.0 SugestaoIA com histórico e foco
- [ ] 8.0 Tela de revisão: ajustes de tecnologia, aviso e cargo-alvo
- [ ] 9.0 E2E, acessibilidade e suíte completa

## Dependências

- Backend: 1.0 → 2.0 → 3.0 → 4.0. A 5.0 depende só da 1.0 e pode correr em paralelo com 2.0 a 4.0.
- API: 6.0 depende de 4.0 e 5.0.
- Frontend: 7.0 e 8.0 dependem de 6.0 (podem correr em paralelo) → 9.0.

| Tarefa | Complexidade | Depende de |
|---|---|---|
| 1.0 | medium | — |
| 2.0 | medium | 1.0 |
| 3.0 | medium | 2.0 |
| 4.0 | high | 3.0 |
| 5.0 | high | 1.0 |
| 6.0 | medium | 4.0, 5.0 |
| 7.0 | medium | 6.0 |
| 8.0 | medium | 6.0 |
| 9.0 | medium | 7.0, 8.0 |

## Decisões adotadas

- Cada tarefa deixa a suíte verde: quem muda a assinatura de uma porta atualiza na mesma tarefa os dublês de teste e os de `src/jobsync/tests/e2e/app_e2e.py`.
- Contratos de API só ganham campos opcionais nos pedidos e campos novos nas respostas (task 6.0). Nenhum campo é removido.
- Distribuição das trocas: todas as ocorrências menos a última da ordem do perfil (PRD, questão em aberto 1, proposta adotada até decisão contrária).
- Ordem das experiências: a do cadastro. Não há ordenação por período nesta JOB.
- Falha do identificador de equivalências não interrompe a adaptação (plano vazio).
- Regenerar o `schema.d.ts` com Python 3.12, o mesmo do CI.
- Fonte PDF: só cargo-alvo e regra de responsabilidades implícitas; sem trocas.

## Desvios em relação à Tech Spec

- **Task 1.0 — vaga externa:** `CandidatarNaVagaExterna` também chamava `ajustar_secao` e não estava listado. Passou a montar um `ContextoVaga` com o `cargo_alvo`. Efeito colateral: como `ContextoVaga` valida o idioma, um idioma diferente de "pt" ou "en" nesse fluxo agora gera 422 (o router já converte `ValueError`). Antes, a adaptação seguia com um nome de idioma desconhecido no prompt.
- **Task 1.0 — linha do cargo-alvo no prompt:** fica em `curriculo/adapters/prompt_contexto_vaga.py` (`linha_cargo_alvo`), usada pelos dois adapters. Sem cargo-alvo, o prompt não muda.
- **Task 2.0 — `ManutencaoTecnologia`:** o plano guarda as manutenções como VO (`indice_experiencia`, `tecnologia`) em vez da tupla `(int, str)` da tech spec, para ficar legível e simétrico a `AjusteTecnologia`.
- **Task 2.0 — uma equivalência por original:** se a IA devolver duas equivalências para a mesma tecnologia original (ex.: React → Angular e React → Vue), só a primeira é usada. Sem isso, a mesma experiência receberia duas trocas conflitantes.
- **Task 2.0 — limitação conhecida:** a comparação por palavra inteira reconhece "React" dentro de "React Native". Não tratado nesta JOB.

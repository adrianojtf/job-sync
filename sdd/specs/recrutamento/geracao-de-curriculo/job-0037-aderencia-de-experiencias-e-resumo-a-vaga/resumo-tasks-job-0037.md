# Resumo de Tarefas de Implementação de Aderência das Experiências e do Resumo à Vaga (JOB-0037)

## Tarefas

- [x] 1.0 Cargo-alvo no ContextoVaga e portas com ContextoVaga
- [x] 2.0 Equivalências e plano de adaptação no domínio
- [x] 3.0 Identificador de equivalências (porta e adapter)
- [x] 4.0 Trocas, cargo-alvo e responsabilidades implícitas na adaptação
- [x] 5.0 Refino variável no backend
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
- **Task 3.0 — dublê de E2E adiado:** o dublê do identificador entra na task 4.0, junto com a injeção em `AdaptarCurriculoParaVaga`. Criá-lo na 3.0 deixaria uma classe sem uso.
- **Task 3.0 — sem chamada desnecessária:** o adapter não chama a IA quando a vaga não tem requisitos ou nenhuma experiência tem descrição; devolve lista vazia.
- **Task 3.0 — formato inválido:** qualquer item fora do formato (inclusive original igual ao alvo) faz o adapter levantar `ValueError`. A task 4.0 trata essa falha como plano vazio, sem interromper a adaptação.
- **Task 4.0 — Streamlit sem mudança:** o app Streamlit monta `AdaptarCurriculoParaVaga` sem ajustador de experiências, então não gera plano. Não precisou da injeção do identificador.
- **Task 4.0 — `equivalencias_aplicadas`:** o plano expõe as equivalências trocadas em ao menos uma experiência (sem repetição). É o que as seções de texto recebem como `ajustes`.
- **Task 4.0 — invariante do rascunho:** `ajustes_tecnologia` só aceita índices de experiências estruturadas existentes.
- **Task 4.0 — exceção explícita no prompt de sistema do ajuste de texto:** "sem inventar tecnologia" passou a excluir as equivalências indicadas na instrução da seção.
- **Task 4.0 — citação explícita genérica:** o prompt pede para citar a tecnologia "dizendo em que parte do trabalho foi usada", em vez do exemplo fixo "no front-end", para servir também a bancos, mensageria etc.
- **Task 4.0 — E2E:** o Playwright completo (19 testes) rodou verde com os novos dublês, inclusive `IdentificadorEquivalenciasE2E` (React → Angular quando a vaga cita Angular).
- **Task 5.0 — limite das sugestões anteriores:** o VO `PedidoRefino` valida tentativa e quantidade (até 3, descartando itens em branco). O limite de 5.000 caracteres de cada sugestão anterior fica nos validadores dos casos de uso (`validar_refino`), porque a constante pertence à camada de serviço.
- **Task 5.0 — routers:** os três endpoints passaram a ler `SugestaoRefinada.valor`, sem mudar o contrato. `refino` e `foco` entram na API na task 6.0.
- **Task 5.0 — trecho de prompt único:** foco e versões anteriores vêm de `curriculo/adapters/prompt_refino.py` (`bloco_refino`), usado pelos três adapters.
- **Task 5.0 — sugestão de experiência na revisão:** `refinar` não recebe o plano de trocas; mantém as tecnologias já citadas por instrução ("Mantenha as tecnologias já citadas nas conquistas e no contexto atuais"), como previsto na tech spec.
- **Achado fora do escopo:** `curriculo_router.py` importa `SalvarCurriculo` sem uso (anterior a esta JOB). Não alterado.

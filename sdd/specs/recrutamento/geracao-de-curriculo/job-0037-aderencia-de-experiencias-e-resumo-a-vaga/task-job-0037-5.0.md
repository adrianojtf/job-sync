# Tarefa 5.0: Refino variável no backend

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

As sugestões de IA passam a partir do texto atual com um foco diferente a cada pedido e sem repetir as sugestões anteriores. Na revisão, a seção deixa de usar o prompt de geração inicial.

<requirements>
- `FocoRefino` e `PedidoRefino` (tentativa >= 1; até 3 anteriores, cada uma dentro de `LIMITE_CARACTERES_SUGESTAO`; `foco(com_vaga)` em rodízio).
- `AjustadorTextoPort.refinar_secao(secao, contexto, refino)` com prompt próprio ("Texto atual", foco, anteriores).
- `AjustadorExperienciaPort.refinar(experiencia, contexto, refino)`: mantém as tecnologias já citadas.
- `MelhoradorTextoCurriculoPort.melhorar_secao(secao, refino)` e `melhorar_experiencia(experiencia, refino)`.
- Os três casos de uso de sugestão recebem `PedidoRefino` (padrão: tentativa 1, sem anteriores) e devolvem `SugestaoRefinada` com o foco usado; seção com vaga chama `refinar_secao`.
- `registrar_sugestao` registra tentativa e foco.
- Complexidade: high. Dependências: 1.0.
</requirements>

## Subtarefas

- [x] 5.1 Testes de `PedidoRefino` e do rodízio (Red).
- [x] 5.2 `FocoRefino`, `PedidoRefino`, `SugestaoRefinada`.
- [x] 5.3 Portas e adapters (texto, experiência, melhorador).
- [x] 5.4 Casos de uso e registro.
- [x] 5.5 Dublês de E2E com saída que varia pelo foco.

## Detalhes de Implementação

Ver "Refino" e "Regras dos prompts" em `techspec-job-0037.md`.

## Critérios de Sucesso

- Tentativas 1 a 4 com vaga dão quatro focos diferentes; sem vaga, três.
- O prompt de refino de seção não contém "Conteúdo original".
- Pedido sem `refino` funciona como hoje (tentativa 1).

## Testes da Tarefa

- [x] Testes de unidade dos VOs, adapters e dos três casos de uso.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/refino.py` (novo)
- `src/jobsync/curriculo/domain/{ajustador_texto_port.py,ajustador_experiencia_port.py,melhorador_texto_curriculo_port.py}`
- `src/jobsync/curriculo/adapters/{ajustador_texto_client.py,ajustador_experiencia_openai_client.py,melhorador_texto_curriculo_openai_client.py}`
- `src/jobsync/curriculo/service_layer/{sugerir_ajuste_experiencia,sugerir_ajuste_experiencia_adaptada,sugerir_ajuste_secao_curriculo}/`, `validacoes_sugestao.py`
- `src/jobsync/tests/curriculo/`, `src/jobsync/tests/e2e/app_e2e.py`

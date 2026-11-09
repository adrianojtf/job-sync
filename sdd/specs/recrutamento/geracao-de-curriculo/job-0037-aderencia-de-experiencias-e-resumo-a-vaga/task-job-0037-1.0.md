# Tarefa 1.0: Cargo-alvo no ContextoVaga e portas com ContextoVaga

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Refatoração sem mudança de comportamento. `ContextoVaga` ganha `cargo_alvo`, e as portas de ajuste passam a receber um `ContextoVaga` no lugar de `descricao_vaga`, `idioma_alvo` e `analise_vaga` soltos. É a base das demais tarefas.

<requirements>
- `ContextoVaga.cargo_alvo: str = ""`, aparado.
- `AjustadorExperienciaPort.ajustar(experiencia, contexto)` e `refinar(experiencia, contexto)`.
- `AjustadorTextoPort.ajustar_secao(secao, contexto)`.
- `AdaptarCurriculoParaVaga` monta o `ContextoVaga` com o `cargo_alvo` do input DTO e o repassa às portas.
- Casos de uso de sugestão repassam o `ContextoVaga` que já recebem.
- Os adapters passam a citar o cargo-alvo no prompt de usuário quando ele vier preenchido (PRD RF9).
- Dublês de teste e de `app_e2e.py` atualizados.
- Complexidade: medium. Dependências: nenhuma.
</requirements>

## Subtarefas

- [ ] 1.1 Testes de `ContextoVaga` com `cargo_alvo` e dos adapters com o cargo no prompt (Red).
- [ ] 1.2 `ContextoVaga`.
- [ ] 1.3 Assinaturas das portas, adapters e casos de uso.
- [ ] 1.4 Dublês de teste e de E2E.

## Detalhes de Implementação

Ver "Interfaces Principais" e decisão 3 ("Portas recebem `ContextoVaga`") em `techspec-job-0037.md`.

## Critérios de Sucesso

- Suíte de backend verde, sem mudança no texto gerado além da linha do cargo-alvo.
- Nenhuma porta recebe mais os três parâmetros soltos.

## Testes da Tarefa

- [ ] Testes de unidade de `ContextoVaga`, dos adapters e de `AdaptarCurriculoParaVaga`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/{contexto_vaga.py,ajustador_experiencia_port.py,ajustador_texto_port.py}`
- `src/jobsync/curriculo/adapters/{ajustador_experiencia_openai_client.py,ajustador_texto_client.py}`
- `src/jobsync/curriculo/service_layer/{adaptar_curriculo_para_vaga,sugerir_ajuste_experiencia_adaptada,sugerir_ajuste_secao_curriculo}/`
- `src/jobsync/tests/curriculo/`, `src/jobsync/tests/e2e/app_e2e.py`

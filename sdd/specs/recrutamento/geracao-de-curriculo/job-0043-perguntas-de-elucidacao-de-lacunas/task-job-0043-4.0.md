# Tarefa 4.0: Comando AdicionarConquistaAExperiencia e endpoint

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Grava a conquista aprovada no banco da experiência escolhida, com origem `RESPOSTA_PERGUNTA`, sem sobrescrever o resto do perfil.

<requirements>
- `PerfilEstruturado.com_conquista_na_experiencia(indice, conquista)` devolve o perfil novo; índice inválido levanta erro de domínio; duplicata é rejeitada pela regra da JOB-0042.
- Service `AdicionarConquistaAExperiencia` em `perfil_estruturado/service_layer/adicionar_conquista_a_experiencia/` com `executar`, usando `PerfilEstruturadoRepository`; perfil inexistente levanta erro.
- `POST /perfil-estruturado/experiencias/{indice}/conquistas`: entrada `{texto}`; saída com o perfil atualizado; 404 para perfil ou índice inexistente e 422 para texto vazio.
- A origem gravada é sempre `RESPOSTA_PERGUNTA`.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 4.1 Escrever os testes do método de domínio (red); implementar (green).
- [x] 4.2 Escrever os testes do service com o repositório falso existente (red); implementar (green).
- [x] 4.3 Escrever os testes do router (red); implementar o endpoint e a injeção (green).
- [x] 4.4 Refatorar e rodar os testes de `perfil_estruturado` e `entrypoints/api`.

## Detalhes de Implementação

Techspec: "Visão Geral dos Componentes" e "Decisões Principais" (comando próprio, e não `PUT` do perfil inteiro). PRD: RF 10 e 15.

## Critérios de Sucesso

- A conquista aprovada aparece no perfil e é considerada nas próximas adaptações.
- As outras partes do perfil não mudam.

## Testes da Tarefa

- [x] Testes de unidade do domínio e do service (`perfil_estruturado_repository_fake`).
- [x] Testes do router.
- [x] Regressão: `src/jobsync/tests/perfil_estruturado/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/perfil_estruturado/domain/perfil_estruturado.py`
- `src/jobsync/perfil_estruturado/adapters/perfil_estruturado_repository_fake.py`
- `src/jobsync/perfil_estruturado/service_layer/adicionar_conquista_a_experiencia/ (novo)`
- `src/jobsync/entrypoints/api/routers/perfil_estruturado_router.py`

## Resultado da execução

- `PerfilEstruturado.com_conquista_na_experiencia`, exceções de domínio (`PerfilEstruturadoNaoEncontrado`, `ExperienciaNaoEncontrada`) e o caso de uso `AdicionarConquistaAExperiencia` (origem `RESPOSTA_PERGUNTA`).
- Endpoint `POST /v1/perfil-estruturado/{perfil_identificador}/experiencias/{experiencia_indice}/conquistas`, com o perfil no caminho para a autorização por perfil valer.

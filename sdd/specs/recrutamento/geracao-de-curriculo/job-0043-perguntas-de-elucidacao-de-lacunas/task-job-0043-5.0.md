# Tarefa 5.0: Resumo usando as conquistas do histórico

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Permite ao resumo usar as conquistas aprovadas como fatos sustentados, mantendo as regras da JOB-0040 (60 palavras, sem cópia, sem fato inventado).

<requirements>
- `ContextoVaga.conquistas_do_historico: tuple[str, ...] = ()`.
- `AjustadorTextoClient`: o prompt do Perfil inclui as conquistas como base de fatos, com a instrução de usar só o que elas e o histórico sustentam; as outras seções não recebem o bloco.
- Sem conquistas, o prompt fica igual ao da JOB-0040.
- O router preenche `conquistas_do_historico` com as conquistas do perfil na adaptação.
- Limite de tamanho do bloco definido em constante nomeada (mais recentes), se a avaliação indicar.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 5.1 Escrever os testes do `ContextoVaga` e do prompt do Perfil (red).
- [x] 5.2 Implementar o campo e o bloco no prompt (green).
- [x] 5.3 Escrever o teste do router e preencher o campo (red e green).
- [x] 5.4 Rodar a regressão da JOB-0040 e de `curriculo`.

## Detalhes de Implementação

Techspec: "Pontos de Integração" (resumo) e "Decisões Principais" (conquistas do banco no contexto). PRD: RF 13.

## Critérios de Sucesso

- O resumo pode citar tema vindo de uma conquista aprovada.
- Nenhuma regressão nos testes da JOB-0040.

## Testes da Tarefa

- [x] Testes de unidade em `src/jobsync/tests/curriculo/test_ajustador_texto_client.py`.
- [x] Teste do router.
- [x] Regressão: `src/jobsync/tests/curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/contexto_vaga.py`
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/tests/curriculo/test_ajustador_texto_client.py`

## Resultado da execução

- `ContextoVaga.conquistas_do_historico`, preenchido pelo caso de uso de adaptação a partir das experiências recebidas (e não pelo router), e bloco no prompt do Perfil e do refino do Perfil; teto de 15 conquistas (`LIMITE_DE_CONQUISTAS_NO_RESUMO`).
- Acréscimo à tarefa: as conquistas também contam como evidência para as Competências (JOB-0044), então uma tecnologia citada numa conquista aprovada deixa de ser lacuna.

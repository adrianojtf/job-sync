# Tarefa 1.0: Regra do resumo aderente no prompt do Perfil

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Troca a instrução da seção Perfil em `AjustadorTextoClient` por uma regra que cobre os temas da vaga e o senso comum do cargo, sem copiar a vaga nem inventar fatos.

<requirements>
- Nova constante `REGRA_RESUMO_ADERENTE_A_VAGA` em `prompt_contexto_vaga.py`, ao lado de `REGRA_RESPONSABILIDADES_IMPLICITAS`.
- `_INSTRUCOES_POR_TIPO[TipoSecao.PERFIL]` usa a nova regra.
- O complemento de tecnologia equivalente do Perfil e a linha do cargo-alvo continuam no prompt.
- As demais seções não recebem a regra do resumo.
- Testes seguem `.windsurf/rules/testing-rules.md`.
</requirements>

## Subtarefas

- [x] 1.1 Escrever os testes de prompt do Perfil (red): traz a regra, o cargo-alvo e o complemento de equivalência.
- [x] 1.2 Escrever o teste de isolamento: as outras seções não recebem a regra.
- [x] 1.3 Criar a constante e usá-la em `ajustador_texto_client.py` (green).
- [x] 1.4 Refatorar e rodar os testes de `curriculo`.

## Detalhes de Implementação

Techspec: "Componentes", "Interfaces Principais" e "Abordagem de Testes". PRD: RF 1 a 5 e 7.

## Critérios de Sucesso

- O prompt do Perfil pede resumo curto, com temas da vaga e do cargo, sem cópia e sem fato inventado.
- Nenhum teste existente de `test_ajustador_texto_client.py` quebra.

## Testes da Tarefa

- [x] Testes de unidade em `test_ajustador_texto_client.py`.
- [x] Regressão: `src/jobsync/tests/curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/adapters/prompt_contexto_vaga.py`
- `src/jobsync/tests/curriculo/test_ajustador_texto_client.py`

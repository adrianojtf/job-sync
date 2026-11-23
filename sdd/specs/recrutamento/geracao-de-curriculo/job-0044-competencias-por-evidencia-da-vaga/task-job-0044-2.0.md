# Tarefa 2.0: Prompt: tirar a frase "todas as tecnologias" e pôr a lista permitida na instrução de tecnologias

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Remove de `_solicitar` a obrigação de citar todas as tecnologias da vaga e passa à instrução de tecnologias o conjunto permitido.

Complexidade: medium.

<requirements>
- Nenhum prompt traz a frase "todas as tecnologias" nem "Cada tecnologia da análise de vaga deve aparecer".
- A instrução de `TECNOLOGIAS` lista os itens permitidos, pede ordenar pela relevância à vaga e proíbe item fora da lista.
- `AjustadorTextoPort.ajustar_secao` ganha `itens_permitidos` opcional; fakes de teste atualizados.
- O refino de tecnologias ("Sugestões de IA") usa as mesmas regras; as demais seções não mudam.
</requirements>

## Subtarefas

- [x] 2.1 Testes de prompt (red): sem a frase obrigatória; tecnologias com a lista e a proibição; outras seções inalteradas.
- [x] 2.2 Alterar `ajustador_texto_client.py` e `ajustador_texto_port.py` (green).
- [x] 2.3 Atualizar os fakes do port nos testes existentes.
- [x] 2.4 Refatorar.

## Detalhes de Implementação

Techspec: "Design de Implementação" e "Abordagem de Testes". PRD: requisitos funcionais correspondentes.

## Critérios de Sucesso

- Os requisitos acima passam nos testes da tarefa.
- Nenhuma regressão nas JOB-0037, JOB-0040 e JOB-0041.

## Testes da Tarefa

- [x] Testes de unidade de `test_ajustador_texto_client.py`.
- [x] Regressão: `src/jobsync/tests/curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/domain/ajustador_texto_port.py`
- `src/jobsync/tests/curriculo/test_ajustador_texto_client.py`

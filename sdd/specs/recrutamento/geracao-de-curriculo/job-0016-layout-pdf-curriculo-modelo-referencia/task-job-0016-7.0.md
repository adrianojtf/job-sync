# Tarefa 7.0: Prompts de IA — preservar quebras de linha e tópicos `-`

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Garantir que o texto que chega ao gerador de PDF tenha a estrutura de linhas e tópicos. Hoje a IA junta os tópicos `-` em prosa e a seção de tecnologias em uma linha só, e o novo layout não tem o que formatar.

<requirements>
- `AjustadorTextoClient`: regra geral de preservação de linhas e tópicos `-` (RF 28).
- `AjustadorTextoClient`, seção `TECNOLOGIAS`: uma categoria por linha no formato `Rótulo: itens` (RF 29).
- Fora desta task: a instrução da seção `EXPERIENCIAS` e o `AjustadorExperienciaOpenAIClient`, que o JOB-0035 já implementou na `main` (RF 30).
- `ExtratorCurriculoClient`: preservar quebras de linha e converter `●`/`•` em `- ` (RF 31).
- Usar o texto sugerido na seção "Ajustes de prompt" da techspec.
- Não alterar as regras atuais de não inventar fatos.
- Sem mudança de modelo, de chamada ou de formato JSON de resposta.
</requirements>

## Subtarefas

- [x] 7.1 Escrever testes que capturam os prompts enviados ao `ClienteOpenAI` (mock com `unittest.mock`) e verificam as novas regras (red).
- [x] 7.2 Atualizar `AjustadorTextoClient`.
- [x] 7.3 Atualizar `ExtratorCurriculoClient`.

## Detalhes de Implementação

Consultar em `techspec-job-0016.md` a seção "Ajustes de prompt".

## Critérios de Sucesso

- Os prompts enviados contêm as regras de preservação.
- Testes existentes dos três clients continuam verdes.

## Testes da Tarefa

- [x] `AjustadorTextoClient`: prompt contém a regra de tópicos `-` para qualquer seção.
- [x] `AjustadorTextoClient`: prompt de `TECNOLOGIAS` contém a regra de uma categoria por linha.
- [x] `ExtratorCurriculoClient`: prompt contém a regra de quebras de linha e marcadores.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/adapters/extrator_curriculo_client.py`
- `src/jobsync/tests/curriculo/test_ajustador_texto_client.py`
- `src/jobsync/tests/curriculo/` (teste do `ExtratorCurriculoClient`, criar se não existir)

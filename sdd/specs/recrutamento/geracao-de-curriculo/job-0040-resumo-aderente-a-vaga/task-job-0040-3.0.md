# Tarefa 3.0: Ajuste da regra do resumo após a avaliação manual

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

A avaliação manual com a vaga Forward Deployed Engineer Sênior mostrou resumo com mais de 200 palavras, listas copiadas da vaga, temas sem base no perfil e o título da vaga ignorado. Esta tarefa troca a redação de `REGRA_RESUMO_ADERENTE_A_VAGA` pelos requisitos revisados do PRD (RF 2 a 9).

<requirements>
- A regra pede no máximo 60 palavras, em um único parágrafo de até 3 frases.
- A regra proíbe listas de termos, ponto e vírgula e referências à vaga ou à oportunidade.
- A regra limita a 3 os temas da vaga, escritos como ações do candidato.
- A regra manda descrever o candidato na linha do cargo-alvo, sem declarar como título um cargo que ele não exerceu.
- A regra manda omitir tema sem sustentação no histórico.
- O Perfil não recebe a ordem genérica "inclua todas as tecnologias da vaga" (causa provável da cópia de termos); as demais seções continuam recebendo.
- O refino do Perfil, em qualquer foco, respeita a regra; o foco "palavras-chave" não pode induzir a copiar trechos da vaga no resumo.
- As demais seções não recebem a regra do resumo.
- Testes seguem `.windsurf/rules/testing-rules.md`.
</requirements>

## Subtarefas

- [x] 3.1 Escrever os testes de prompt do Perfil (red): limite de 60 palavras, proibição de listas e de ponto e vírgula, limite de 3 temas, cargo-alvo como eixo e omissão do que o histórico não sustenta.
- [x] 3.2 Escrever o teste do refino do Perfil com foco "palavras-chave": o prompt mantém a proibição de copiar trechos da vaga.
- [x] 3.3 Ajustar a constante e, se o teste 3.2 exigir, a instrução do foco no resumo (green).
- [x] 3.4 Refatorar e rodar os testes de `curriculo`.
- [ ] 3.5 (a cargo do usuário, com chaves reais) Repetir a avaliação manual com as vagas de teste, incluindo a FDE Sênior, e registrar o resultado na tabela da task 2.0.

## Detalhes de Implementação

Techspec: "Atualização após a avaliação manual". PRD: RF 2 a 9 e Questões em Aberto 3 e 4.

## Critérios de Sucesso

- O prompt do Perfil traz o limite de 60 palavras, as proibições de forma e o cargo-alvo como eixo.
- Na avaliação manual, nenhum resumo passa de 60 palavras, copia trechos da vaga ou afirma o que o perfil não sustenta.
- Nenhum teste existente de `test_ajustador_texto_client.py` quebra.

## Testes da Tarefa

- [x] Testes de unidade em `test_ajustador_texto_client.py`.
- [x] Regressão: `src/jobsync/tests/curriculo/`.
- [ ] Avaliação manual registrada na task 2.0 (não há teste automatizado da qualidade do texto).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/prompt_contexto_vaga.py`
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/adapters/prompt_refino.py`
- `src/jobsync/tests/curriculo/test_ajustador_texto_client.py`

## Resultado da execução

- Causa adicional encontrada: o prompt genérico de `AjustadorTextoClient._solicitar` mandava incluir no texto "todas as tecnologias" da análise da vaga, mesmo ausentes do conteúdo original, em qualquer seção, inclusive no Perfil. Isso contradiz a regra do resumo e explica a lista de termos copiados. Agora o Perfil recebe uma instrução oposta (só tecnologias que o histórico sustenta); as outras seções ficam iguais.
- `REGRA_RESUMO_ADERENTE_A_VAGA` reescrita com os requisitos do PRD (60 palavras, sem listas, 3 temas, cargo-alvo como eixo, omissão do que não é sustentado).
- Testes: `src/jobsync/tests/curriculo/` com 363 testes passando.
- Pendente (3.5, a cargo do usuário): repetir a avaliação manual com chaves reais, incluindo a vaga FDE Sênior.

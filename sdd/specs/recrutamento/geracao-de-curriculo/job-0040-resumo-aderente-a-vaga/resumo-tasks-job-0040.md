# Resumo de Tarefas de Implementação do Resumo Aderente à Vaga (JOB-0040)

## Tarefas

- [x] 1.0 Regra do resumo aderente no prompt do Perfil
- [x] 2.0 Reuso da regra no refino do Perfil e avaliação manual
- [x] 3.0 Ajuste da regra do resumo após a avaliação manual

## Dependências

- 1.0 não depende de nenhuma outra tarefa.
- 2.0 depende da 1.0.
- 3.0 depende da 1.0 e da 2.0.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Regra do resumo aderente no prompt do Perfil | low | — | `test_ajustador_texto_client`: o prompt do Perfil traz a regra, o cargo-alvo e o complemento de tecnologia equivalente; as outras seções não recebem a regra. |
| 2.0 | Reuso da regra no refino do Perfil e avaliação manual | low | 1.0 | `refinar_secao` do Perfil com foco de aderência traz a regra; avaliação manual com vagas de teste. |
| 3.0 | Ajuste da regra do resumo após a avaliação manual | low | 1.0, 2.0 | `test_ajustador_texto_client`: o prompt do Perfil traz limite de 60 palavras, proibição de listas e de ponto e vírgula, limite de 3 temas, cargo-alvo como eixo e omissão do que o histórico não sustenta; o refino com foco "palavras-chave" mantém a proibição de copiar a vaga. |

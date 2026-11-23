# Resumo de Tarefas de Implementação do Resumo Aderente à Vaga (JOB-0040)

## Tarefas

- [x] 1.0 Regra do resumo aderente no prompt do Perfil
- [x] 2.0 Reuso da regra no refino do Perfil e avaliação manual

## Dependências

- 1.0 não depende de nenhuma outra tarefa.
- 2.0 depende da 1.0.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Regra do resumo aderente no prompt do Perfil | low | — | `test_ajustador_texto_client`: o prompt do Perfil traz a regra, o cargo-alvo e o complemento de tecnologia equivalente; as outras seções não recebem a regra. |
| 2.0 | Reuso da regra no refino do Perfil e avaliação manual | low | 1.0 | `refinar_secao` do Perfil com foco de aderência traz a regra; avaliação manual com vagas de teste. |

# Tarefa 2.0: Reuso da regra no refino do Perfil e avaliação manual

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Faz o botão "Sugestões de IA" do resumo respeitar a mesma regra, e valida a qualidade do texto com vagas de teste.

<requirements>
- `refinar_secao` do Perfil inclui a regra do resumo em qualquer foco, porque a instrução da seção já entra no prompt do refino; não há mudança em `prompt_refino.py`.
- As outras seções não mudam.
- Avaliação manual com ao menos três vagas: engenharia de software, Forward Deployed Engineer e cargo fora de TI.
</requirements>

## Subtarefas

- [x] 2.1 Escrever os testes do refino do Perfil: a regra aparece em todos os focos e o texto atual é a base (passaram de primeira: o comportamento já existia).
- [x] 2.2 Confirmar que `prompt_refino.py` e `refinar_secao` não precisam de ajuste.
- [ ] 2.3 Rodar a avaliação manual: temas cobertos, sem cópia da vaga, sem fato inventado, até o limite de tamanho.
- [ ] 2.4 Ajustar a redação da regra conforme a avaliação e registrar o resultado e as vagas usadas no fim deste arquivo.
- [ ] 2.5 Fechar as questões em aberto 1 e 2 do PRD (tamanho máximo e limite do senso comum) com o resultado.

## Detalhes de Implementação

Techspec: "Decisões Principais" (reuso no refino) e "Avaliação manual". PRD: RF 6 e Questões em Aberto.

## Critérios de Sucesso

- O refino do resumo com foco de aderência segue a mesma regra da geração.
- Na avaliação manual, nenhum resumo copia trechos da vaga nem afirma o que o perfil não sustenta.
- Nenhuma regressão nos testes das JOB-0034 e JOB-0037.

## Testes da Tarefa

- [x] Testes de unidade do refino.
- [x] Regressão: `src/jobsync/tests/curriculo/`.
- [ ] Avaliação manual registrada neste arquivo (não há teste automatizado da qualidade do texto).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/prompt_refino.py`
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/domain/refino.py`
- `src/jobsync/tests/curriculo/test_ajustador_texto_client.py`

## Roteiro da avaliação manual (2.3 a 2.5)

Pendente: exige `OPENAI_API_KEY` e `TYPESAFE_API_KEY` reais, que o ambiente de desenvolvimento da IA não tem. Executar localmente, com o perfil real, em "Ajustar para uma vaga".

Vagas de teste: engenharia de software (arquitetura hexagonal e code review), Forward Deployed Engineer e um cargo fora de TI. Há exemplos em `files_examples/vaga-teste.txt`.

Para cada vaga, gerar o currículo adaptado, ler o resumo na revisão e pedir "Sugestões de IA" duas vezes. Conferir:

- [ ] Cobre os temas centrais da vaga e do cargo, de forma natural.
- [ ] Não copia trechos da vaga.
- [ ] Não afirma anos de experiência, cargos ou métricas que o perfil não sustenta.
- [ ] Tem até 3 frases (e cerca de 60 palavras).
- [ ] As sugestões de IA mantêm a regra.

Resultado por vaga (preencher): | Vaga | Resumo gerado | Cobertura | Cópia | Fato inventado | Tamanho |

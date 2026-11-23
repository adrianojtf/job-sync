# Tarefa 2.0: Reuso da regra no refino do Perfil e avaliação manual

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Faz o botão "Sugestões de IA" do resumo respeitar a mesma regra, e valida a qualidade do texto com vagas de teste.

<requirements>
- `refinar_secao` do Perfil com foco `ADERENCIA_VAGA` inclui a regra do resumo; as outras seções e os outros focos não mudam.
- A forma de passar a regra a `bloco_refino` é decidida no TDD (primeira opção: passar o tipo da seção).
- Avaliação manual com ao menos três vagas: engenharia de software, Forward Deployed Engineer e cargo fora de TI.
</requirements>

## Subtarefas

- [ ] 2.1 Escrever os testes do refino do Perfil (red): foco de aderência traz a regra; outras seções não.
- [ ] 2.2 Ajustar `prompt_refino.py` e `refinar_secao` (green).
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

- [ ] Testes de unidade do refino.
- [ ] Regressão: `src/jobsync/tests/curriculo/`.
- [ ] Avaliação manual registrada neste arquivo (não há teste automatizado da qualidade do texto).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/prompt_refino.py`
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/domain/refino.py`
- `src/jobsync/tests/curriculo/test_ajustador_texto_client.py`

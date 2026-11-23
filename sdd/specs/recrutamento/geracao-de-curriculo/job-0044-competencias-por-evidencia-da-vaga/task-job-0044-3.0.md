# Tarefa 3.0: Serviço de adaptação: seleção antes da IA, filtro e teto depois, e `lacunas_tecnologia`

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Liga o domínio ao fluxo: calcula a seleção, restringe a saída da IA ao conjunto permitido, aplica o teto e devolve as lacunas no rascunho.

Complexidade: high.

<requirements>
- `AdaptarCurriculoParaVaga` calcula a seleção com os itens da seção de tecnologias, os textos das experiências, os requisitos da vaga e as equivalências do plano.
- O conjunto permitido segue para `ajustar_secao`; o que a IA acrescentar fora dele é descartado.
- O teto de 45 é aplicado às categorias; os relevantes são os requisitos da vaga.
- `RascunhoCurriculoAdaptado.lacunas_tecnologia` recebe as lacunas; sem seção de tecnologias, não há lacunas.
- Log `info` só com contagens.
</requirements>

## Subtarefas

- [x] 3.1 Testes do serviço com fakes (red): item acrescentado pela IA é descartado; teto; lacunas; fonte PDF; sem seção de tecnologias.
- [x] 3.2 Testes do rascunho com `lacunas_tecnologia` (red).
- [x] 3.3 Implementar no serviço e no rascunho (green).
- [x] 3.4 Refatorar.

## Detalhes de Implementação

Techspec: "Design de Implementação" e "Abordagem de Testes". PRD: requisitos funcionais correspondentes.

## Critérios de Sucesso

- Os requisitos acima passam nos testes da tarefa.
- Nenhuma regressão nas JOB-0037, JOB-0040 e JOB-0041.

## Testes da Tarefa

- [x] Testes de unidade do serviço e do rascunho.
- [x] Regressão: `src/jobsync/tests/curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/service.py`
- `src/jobsync/curriculo/domain/rascunho_curriculo_adaptado.py`
- `src/jobsync/tests/curriculo/test_adaptar_curriculo_para_vaga_service.py`

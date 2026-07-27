# Tarefa 4.0: Criar testes de unidade para o novo fluxo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar uma suíte de testes de unidade para validar o novo componente de análise de vaga, a integração com o caso de uso `AdaptarCurriculoParaVaga` e a atualização de `AjustadorTextoGroq`.

<requirements>
- Adicionar testes para `JobDescriptionAnalyzerGroq` com um stub/fake de `ClienteGroq`.
- Adicionar testes para o caso de uso estendido de adaptação de currículo.
- Verificar o comportamento dos prompts para a seção de tecnologias.
</requirements>

## Subtarefas

- [ ] 4.1 Escrever testes de unidade para `JobDescriptionAnalyzerGroq`.
- [ ] 4.2 Escrever testes para `AdaptarCurriculoParaVaga` com um fake `JobDescriptionAnalyzerPort`.
- [ ] 4.3 Escrever testes para `AjustadorTextoGroq` validando a passagem do contexto de análise de vaga.

## Detalhes de Implementação

Usar o padrão de testes existente em `tests/` e manter os novos testes independentes de chamadas de rede. Criar dublês de teste para `ClienteGroq` e `JobDescriptionAnalyzerPort`.

## Critérios de Sucesso

- [ ] Todos os novos testes passam.
- [ ] O comportamento de análise e de ajuste de conteúdo é coberto por casos essenciais.
- [ ] Os testes não dependem de chamadas reais à API Groq.

## Testes da Tarefa

- [ ] Testes de unidade para o adapter e caso de uso.
- [ ] Testes de comportamento do prompt no `AjustadorTextoGroq`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `tests/`
- `application/use_cases/adaptar_curriculo_para_vaga.py`
- `infrastructure/llm/ajustador_texto_groq.py`
- `infrastructure/llm/cliente_groq.py`
- `sdd/specs/recrutamento/analise-de-vagas/job-1234-refinar-coleta-tratamento-ferramentas-especificacoes-vaga/prd-job-1234.md`

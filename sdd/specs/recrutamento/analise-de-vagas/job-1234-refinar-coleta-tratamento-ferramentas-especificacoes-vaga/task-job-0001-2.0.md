# Tarefa 2.0: Implementar o adapter de análise de vaga com Groq

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o adapter `JobDescriptionAnalyzerGroq` em `infrastructure/llm` para enviar prompts ao modelo Groq e receber uma análise estruturada da descrição de vaga.

<requirements>
- Criar o adapter `JobDescriptionAnalyzerGroq` que consome `ClienteGroq`.
- Construir prompts conservadores que extraem somente requisitos explícitos e marquem inferências ambíguas.
- Retornar `AnaliseVaga` conforme definido na task 1.0.
</requirements>

## Subtarefas

- [ ] 2.1 Implementar o prompt para extrair tecnologias, frameworks, bancos de dados e experiência explicitamente mencionados.
- [ ] 2.2 Implementar marcação de itens implícitos ou ambíguos, sem promovê-los automaticamente a requisitos técnicos.
- [ ] 2.3 Tratar respostas JSON inválidas com exceções claras.

## Detalhes de Implementação

Basear a implementação em `infrastructure/llm/cliente_groq.py` e no estilo de prompts usados em `infrastructure/llm/ajustador_texto_groq.py`. O adapter deve permanecer desacoplado do caso de uso.

## Critérios de Sucesso

- [ ] O adapter retorna um objeto `AnaliseVaga` válido para uma descrição de vaga de teste.
- [ ] Requisitos explícitos e implícitos são diferenciados na saída.
- [ ] Erros de parsing JSON são tratados e levantam exceções compreensíveis.

## Testes da Tarefa

- [ ] Criar teste unitário para `JobDescriptionAnalyzerGroq` com um fake de `ClienteGroq`.
- [ ] Validar resposta esperada para uma descrição de vaga de exemplo como a do PRD.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-1234-refinar-coleta-tratamento-ferramentas-especificacoes-vaga/prd-job-1234.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-1234-refinar-coleta-tratamento-ferramentas-especificacoes-vaga/techspec-job-1234.md`
- `infrastructure/llm/cliente_groq.py`
- `infrastructure/llm/ajustador_texto_groq.py`

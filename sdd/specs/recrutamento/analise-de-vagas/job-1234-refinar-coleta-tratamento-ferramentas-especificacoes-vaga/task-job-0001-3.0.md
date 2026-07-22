# Tarefa 3.0: Integrar a análise de vaga ao fluxo de adaptação de currículo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Estender o caso de uso `AdaptarCurriculoParaVaga` e o adaptador de ajuste de texto para usar a análise estruturada da descrição de vaga no processo de adaptação de currículo.

<requirements>
- Modificar `AdaptarCurriculoParaVaga` para receber e usar `AnaliseVaga` antes de ajustar cada seção.
- Atualizar `AjustadorTextoGroq` para aceitar informações de `AnaliseVaga` e ajustar prompts com base em requisitos explícitos e implícitos.
- Manter o fluxo de geração de PDF e os contratos de `Curriculo` existentes.
</requirements>

## Subtarefas

- [ ] 3.1 Estender a assinatura do caso de uso para incluir a análise de vaga.
- [ ] 3.2 Repassar a análise de vaga para `AjustadorTextoGroq` durante `ajustar_secao`.
- [ ] 3.3 Garantir que seções não relacionadas continuem funcionando sem a análise de vaga.

## Detalhes de Implementação

Referenciar o `techspec-job-1234.md` para o fluxo de integração. O design deve preservar o princípio de que o ajuste de currículo se baseia em fatos originais e usa a análise de vaga apenas como contexto adicional.

## Critérios de Sucesso

- [ ] O novo fluxo de adaptação ainda funciona para um currículo de teste com descrição de vaga.
- [ ] `AjustadorTextoGroq` usa dados de análise de vaga para evitar inferências de frameworks não mencionados.
- [ ] O comportamento das seções de currículo existentes não é degradado.

## Testes da Tarefa

- [ ] Teste de unidade que simule `JobDescriptionAnalyzerPort` no caso de uso estendido.
- [ ] Teste de unidade que confirme que o prompt do `AjustadorTextoGroq` contém informações de requisitos explícitos/implícitos.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `application/use_cases/adaptar_curriculo_para_vaga.py`
- `infrastructure/llm/ajustador_texto_groq.py`
- `sdd/specs/recrutamento/analise-de-vagas/job-1234-refinar-coleta-tratamento-ferramentas-especificacoes-vaga/techspec-job-1234.md`

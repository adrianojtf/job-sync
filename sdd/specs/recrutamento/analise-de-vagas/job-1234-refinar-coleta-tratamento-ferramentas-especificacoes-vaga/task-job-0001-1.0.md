# Tarefa 1.0: Definir o modelo de domínio e porta para análise de descrição de vaga

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Definir o contrato de domínio para análise de descrição de vaga que permita classificar requisitos técnicos em explícitos, implícitos e ambiguidade, sem alterar o modelo de currículo existente.

<requirements>
- Criar os modelos de domínio `AnaliseVaga` e `RequisitoTecnico`.
- Criar a porta `JobDescriptionAnalyzerPort` no layer de aplicação.
- Garantir que o modelo preserve o texto original da descrição para auditoria.
</requirements>

## Subtarefas

- [ ] 1.1 Definir o dataclass `RequisitoTecnico` com campos `nome`, `categoria`, `tipo` e `origem`.
- [ ] 1.2 Definir o dataclass `AnaliseVaga` com `requisitos`, `ambiguidade` e `texto_original`.
- [ ] 1.3 Definir a interface `JobDescriptionAnalyzerPort.analisar(descricao_vaga: str) -> AnaliseVaga`.

## Detalhes de Implementação

Referenciar o `techspec-job-1234.md` para entender o formato esperado de saída do serviço de análise de vaga. A implementação deve permanecer isolada em `application/ports` e `domain`.

## Critérios de Sucesso

- [ ] Os novos modelos são imutáveis e fáceis de testar.
- [ ] A porta expõe apenas `analisar(descricao_vaga: str)`.
- [ ] O domínio suporta distinção entre `explícito`, `implícito` e `ambiguidade`.

## Testes da Tarefa

- [ ] Criar testes de unidade que instanciem `RequisitoTecnico` e `AnaliseVaga`.
- [ ] Validar que `JobDescriptionAnalyzerPort` é uma interface pura e não contém lógica de IA.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-1234-refinar-coleta-tratamento-ferramentas-especificacoes-vaga/prd-job-1234.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-1234-refinar-coleta-tratamento-ferramentas-especificacoes-vaga/techspec-job-1234.md`
- `application/ports/ajustador_texto_port.py`
- `domain/curriculo.py`

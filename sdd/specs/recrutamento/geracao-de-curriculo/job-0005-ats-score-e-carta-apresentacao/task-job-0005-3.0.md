# Tarefa 3.0: Definir porta GeradorCartaApresentacaoPort

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Definir a interface de aplicação (Port) para geração de carta de apresentação, seguindo o mesmo padrão de Dependency Inversion já usado por `AjustadorTextoPort` e `JobDescriptionAnalyzerPort`.

<requirements>
- `GeradorCartaApresentacaoPort` deve expor um método `gerar(curriculo, analise_vaga, idioma_alvo) -> str`.
- Interface pura (`ABC` + `@abstractmethod`), sem implementação concreta nesta tarefa — complexidade: low.
</requirements>

## Subtarefas

- [x] 3.1 Criar `application/ports/gerador_carta_apresentacao_port.py` com a interface `GeradorCartaApresentacaoPort`.
- [x] 3.2 Escrever teste unitário confirmando que a porta é uma interface pura (seguindo o padrão de `tests/application/test_job_description_analyzer_port.py`).

## Detalhes de Implementação

Consultar a seção "Interfaces Principais" de `techspec-job-0005.md` para a assinatura exata do método `gerar`.

## Critérios de Sucesso

- A porta compila e pode ser implementada por um fake de teste sem depender da API Groq.

## Testes da Tarefa

- [x] Teste unitário: um fake de `GeradorCartaApresentacaoPort` implementa `gerar` e retorna o texto esperado.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `application/ports/gerador_carta_apresentacao_port.py`
- `tests/application/test_gerador_carta_apresentacao_port.py`

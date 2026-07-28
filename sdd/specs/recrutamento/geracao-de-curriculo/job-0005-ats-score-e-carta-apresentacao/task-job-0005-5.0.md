# Tarefa 5.0: Implementar use case GerarCartaApresentacao

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o caso de uso que orquestra a chamada à porta `GeradorCartaApresentacaoPort`, recebendo o `Curriculo` adaptado, a `AnaliseVaga` (agora exposta em `ResultadoAdaptacao`, Tarefa 2.0) e o idioma alvo.

<requirements>
- `GerarCartaApresentacao` deve receber `GeradorCartaApresentacaoPort` via injeção de dependência no construtor (mesmo padrão de `AdaptarCurriculoParaVaga`).
- O método `executar(curriculo, analise_vaga, idioma_alvo) -> str` apenas repassa os dados à porta, sem lógica de negócio adicional — complexidade: low.
</requirements>

## Subtarefas

- [x] 5.1 Criar `application/use_cases/gerar_carta_apresentacao.py` com a classe `GerarCartaApresentacao`.
- [x] 5.2 Implementar `executar(curriculo, analise_vaga, idioma_alvo) -> str`.
- [x] 5.3 Escrever testes unitários usando um fake de `GeradorCartaApresentacaoPort`, validando que os três parâmetros são repassados corretamente.

## Detalhes de Implementação

Consultar a seção "Visão Geral dos Componentes" de `techspec-job-0005.md` para a responsabilidade exata do use case (apenas orquestração, sem lógica própria).

## Critérios de Sucesso

- O use case repassa corretamente currículo, análise de vaga e idioma para a porta, retornando o texto gerado sem transformação.

## Testes da Tarefa

- [x] Teste unitário: fake de `GeradorCartaApresentacaoPort` recebe exatamente os argumentos passados a `executar`.
- [x] Teste unitário: o texto retornado pela porta é retornado sem alteração pelo use case.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `application/use_cases/gerar_carta_apresentacao.py`
- `tests/application/test_gerar_carta_apresentacao.py`

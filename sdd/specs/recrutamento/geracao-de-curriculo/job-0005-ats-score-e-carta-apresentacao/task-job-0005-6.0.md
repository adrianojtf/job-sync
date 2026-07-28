# Tarefa 6.0: Integrar ATS Score e carta de apresentação na UI Streamlit

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Conectar `CalcularAtsScore` (Tarefa 1.0) e `GerarCartaApresentacao` (Tarefa 5.0) ao fluxo de resultado já existente em `ui/app_streamlit.py`, exibindo nota, requisitos faltantes e botão de download da carta junto do PDF adaptado, sem alterar o comportamento atual de geração do PDF.

<requirements>
- Após `AdaptarCurriculoParaVaga.executar()` retornar (fluxo já existente), chamar em sequência `CalcularAtsScore` e `GerarCartaApresentacao`, usando `resultado.curriculo_adaptado` e `resultado.analise_vaga` (Tarefa 2.0).
- Exibir a nota (0-100) e a lista de requisitos faltantes na mesma tela onde o download do PDF já aparece.
- Exibir botão de download da carta de apresentação, independente do download do PDF.
- Falha na geração da carta não deve impedir o download do PDF já gerado (ATS Score e carta são informativos, não bloqueantes) — complexidade: medium.
</requirements>

## Subtarefas

- [x] 6.1 Instanciar `CalcularAtsScore` e `GerarCartaApresentacao` na Composition Root (`_montar_caso_de_uso` ou função equivalente) de `ui/app_streamlit.py`.
- [x] 6.2 Após a adaptação bem-sucedida, calcular e exibir a nota de ATS Score e os requisitos faltantes.
- [x] 6.3 Gerar e exibir botão de download da carta de apresentação (arquivo `.txt`).
- [x] 6.4 Tratar falha na geração da carta separadamente do fluxo de PDF, exibindo aviso sem interromper o download do currículo.

## Detalhes de Implementação

Consultar a seção "Visão Geral dos Componentes" (fluxo de dados) de `techspec-job-0005.md`. O PDF continua sendo gerado exatamente como hoje; ATS Score e carta são chamadas adicionais após esse resultado, na mesma tela.

## Critérios de Sucesso

- Usuário vê nota, requisitos faltantes e pode baixar a carta na mesma tela onde já baixa o PDF adaptado.
- Fluxo de adaptação existente continua funcionando sem regressão.

## Testes da Tarefa

- [x] Teste manual: gerar uma adaptação e confirmar que nota, requisitos faltantes e carta aparecem corretamente.
- [x] Teste manual: simular falha na geração da carta (ex: API indisponível) e confirmar que o PDF ainda pode ser baixado.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `ui/app_streamlit.py`

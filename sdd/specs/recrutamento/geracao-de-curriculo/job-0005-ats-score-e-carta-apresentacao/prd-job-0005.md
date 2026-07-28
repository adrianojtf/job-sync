# Documento de Requisitos de Produto (PRD)

## Visão Geral

Hoje o job-sync adapta o currículo para uma vaga e entrega o PDF final — mas o usuário não tem nenhuma visibilidade sobre o quão aderente aquele currículo ficou em relação à vaga antes de baixá-lo, nem uma carta de apresentação para acompanhar a candidatura. Este PRD adiciona duas funcionalidades que reaproveitam a análise de vaga (`AnaliseVaga`) já extraída no fluxo existente: uma nota de aderência (ATS Score) com a lista de requisitos não cobertos, e a geração automática de carta de apresentação personalizada. Ambas aparecem como parte do mesmo fluxo de adaptação, sem exigir nova entrada de dados do usuário.

## Objetivos

- Dar ao usuário um indicador objetivo de quão bem o currículo adaptado atende aos requisitos da vaga, antes de enviar a candidatura.
- Reduzir o trabalho manual de escrever uma carta de apresentação para cada vaga.
- Reaproveitar 100% da análise de vaga já feita pelo `JobDescriptionAnalyzerPort`, sem duplicar lógica de extração de requisitos.
- Sucesso é: o usuário vê a nota e os requisitos faltantes junto com o PDF gerado, e pode baixar a carta de apresentação no mesmo clique.

## Histórias de Usuário

1. Como candidato, eu quero ver uma nota de aderência do meu currículo adaptado em relação à vaga, para saber se vale a pena revisar algo antes de enviar.
2. Como candidato, eu quero ver quais requisitos técnicos da vaga não aparecem no meu currículo, para decidir se devo adicioná-los (caso eu realmente tenha aquela experiência) antes de gerar a versão final.
3. Como candidato, eu quero receber uma carta de apresentação já escrita e adaptada à vaga, no mesmo idioma escolhido para o currículo, para não precisar escrever do zero.
4. Como candidato, eu quero poder baixar a carta de apresentação separadamente do currículo, para poder revisar e editar antes de enviar.

## Funcionalidades Principais

### 1. ATS Score

- Após a adaptação do currículo, o sistema calcula uma nota (0-100) de aderência entre o currículo adaptado e os requisitos extraídos da vaga (`AnaliseVaga`).
- A nota considera apenas requisitos técnicos classificados como explícitos na vaga (não penaliza a ausência de requisitos implícitos/ambíguos).
- O sistema lista os requisitos explícitos da vaga que não foram encontrados em nenhuma seção do currículo adaptado.

Requisitos funcionais:
1. O sistema deve calcular e exibir uma nota de 0 a 100 representando a proporção de requisitos técnicos explícitos da vaga presentes no currículo adaptado.
2. O sistema deve listar individualmente os requisitos explícitos da vaga não encontrados no currículo adaptado.
3. O sistema deve exibir a nota e a lista de requisitos faltantes na mesma tela de resultado onde o PDF adaptado é disponibilizado para download.
4. O sistema não deve bloquear o download do currículo com base na nota — o ATS Score é informativo, não um gate.

### 2. Carta de apresentação automática

- O sistema gera um texto de carta de apresentação personalizado, usando a mesma `AnaliseVaga` e o currículo adaptado como contexto, no idioma alvo escolhido pelo usuário.
- A carta segue estrutura padrão (saudação, motivação para a vaga, principais qualificações alinhadas, encerramento), sem inventar fatos que não estejam no currículo original.
- O usuário pode baixar a carta em formato de texto simples ou PDF, separadamente do currículo.

Requisitos funcionais:
5. O sistema deve gerar uma carta de apresentação em texto, personalizada com base na vaga e no currículo adaptado, no idioma alvo selecionado.
6. A carta gerada não deve incluir fatos, tecnologias ou experiências que não constem no currículo original do usuário.
7. O sistema deve permitir o download da carta de apresentação de forma independente do PDF do currículo.
8. O sistema deve gerar a carta automaticamente como parte do mesmo fluxo de adaptação, sem exigir uma ação separada do usuário além da já existente ("Gerar currículo adaptado").

## Experiência do Usuário

Personas:
- Candidato que já usa o adaptador de currículo e quer decidir se o resultado está bom o suficiente para enviar.
- Candidato que não gosta de escrever carta de apresentação e quer um rascunho pronto para revisar.

Jornada principal:
1. Usuário preenche o formulário de adaptação já existente (PDF, descrição da vaga, idioma, cargo, empresa) e clica em "Gerar currículo adaptado".
2. Na tela de resultado, além do link de download do PDF (comportamento atual), aparecem: a nota de ATS Score, a lista de requisitos faltantes, e um botão de download da carta de apresentação.
3. Usuário revisa a nota e os requisitos faltantes; se decidir que o currículo original precisa de ajuste, refaz o upload (fluxo já existente).

Não há requisitos de acessibilidade além dos já suportados pelo Streamlit por padrão.

## Restrições Técnicas de Alto Nível

- Deve reaproveitar a análise de vaga (`AnaliseVaga`) já produzida no fluxo existente, sem uma segunda chamada de extração de requisitos.
- A geração de carta de apresentação depende da mesma integração com a API da Groq já usada para ajuste de texto — não introduz novo provedor de IA.
- Deve preservar a garantia já existente no projeto de não alterar fatos do candidato (mesma regra aplicada ao ajuste de seções do currículo).

## Fora de Escopo

- Edição manual da carta de apresentação dentro da aplicação (o usuário edita fora, no próprio arquivo baixado).
- Histórico de notas de ATS Score entre diferentes candidaturas (fica para uma fase futura que dependa de persistência de perfil).
- Sugestões automáticas de como reescrever o currículo para aumentar a nota (o sistema aponta a lacuna, mas não reescreve sozinho).
- Comparação de ATS Score entre diferentes versões salvas do currículo.

## Questões em Aberto

- A fórmula de nota deve dar peso diferente por categoria de requisito (ex: tecnologia vs. metodologia), ou todos os requisitos explícitos valem o mesmo?
- A carta de apresentação deve ter um limite de tamanho (ex: máximo de palavras) para caber em uma página?
- Quando a vaga não tem nenhum requisito explícito identificado pela análise (só implícitos/ambíguos), qual deve ser o comportamento da nota — 100, ou "não calculável"?

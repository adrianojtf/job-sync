# Documento de Requisitos de Produto (PRD)

## Visão Geral

Este PRD define a correção da geração de currículos para garantir que os rótulos de seções e categorias tecnológicas sejam apresentados na língua selecionada pelo usuário, sem depender de valores fixos em português.

O problema atual é percebido em dois cenários:

- Quando o currículo é gerado em inglês, os rótulos de seções como "Tecnologias", "Perfil" e "Experiências" permanecem em português, mesmo quando o idioma selecionado para o currículo é o inglês.
- Quando o currículo é gerado em português, a seção de tecnologias nem sempre apresenta a estrutura esperada de categorias, como "Linguagens", "Frameworks" e demais grupos, e pode acabar sendo renderizada como uma lista plana ou com rótulos inconsistentes.

A correção deve assegurar que o conteúdo do currículo seja consistente com o idioma de saída e que as categorias de tecnologia sejam organizadas de forma clara e localizadas de acordo com a língua escolhida.

## Objetivos

- Garantir que os rótulos de seções do currículo sejam traduzidos e exibidos conforme o idioma selecionado pelo usuário.
- Garantir que as categorias de tecnologia sejam exibidas corretamente no idioma selecionado, por exemplo:
  - Português: Linguagens, Frameworks, Desenvolvimento Web, DevOps, Bancos de Dados, Controle de Versão e Outros.
  - Inglês: Languages, Frameworks, Web Development, DevOps, Databases, Version Control e Other.
- Preservar o conteúdo técnico original do currículo, sem perder tecnologias, frameworks ou ferramentas já informados.
- Melhorar a legibilidade e a consistência do PDF e do texto final do currículo, reduzindo interpretações ambíguas.
- Manter a correção alinhada ao fluxo atual de geração de currículos, sem exigir uma reestruturação completa do processo.

## Histórias de Usuário

1. Como candidato, eu quero que meu currículo seja gerado em inglês com rótulos de seções em inglês para que a apresentação fique consistente com o idioma escolhido.
2. Como candidato, eu quero que a seção de tecnologias do meu currículo em português seja organizada em categorias claras, como Linguagens e Frameworks, para facilitar a leitura.
3. Como recrutador, eu quero que as categorias de tecnologias apareçam de forma padronizada e traduzida corretamente para avaliar rapidamente o perfil técnico do candidato.
4. Como desenvolvedor do produto, eu quero que a lógica de tradução e agrupamento seja centralizada para evitar divergências entre os diferentes fluxos de geração de currículo.

## Funcionalidades Principais

### 1. Localização dinâmica de seções do currículo

- O sistema deve usar o idioma selecionado para renderizar os rótulos de seções principais, como Tecnologias, Perfil, Experiências e Formação.
- A localização deve ser aplicada de forma consistente para todos os fluxos de geração de currículo, inclusive em versões em PDF e em outros formatos de saída.
- Se um idioma não tiver uma tradução definida para uma seção, o sistema deve aplicar um fallback previsível e controlado.

Requisitos funcionais:
1. Aplicar tradução automática dos rótulos de seções principais conforme o idioma selecionado do currículo.
2. Garantir que as seções de perfil, experiências e tecnologias não permaneçam com rótulos fixos em português quando o idioma for inglês.
3. Definir um mecanismo de fallback para idiomas não cobertos, preservando consistência na interface e no conteúdo.

### 2. Localização dinâmica de categorias de tecnologias

- O sistema deve gerar as categorias de tecnologias no idioma selecionado, por exemplo:
  - Em português: Linguagens, Frameworks, Desenvolvimento Web, DevOps, Bancos de Dados, Controle de Versão e Outros.
  - Em inglês: Languages, Frameworks, Web Development, DevOps, Databases, Version Control e Other.
- As categorias devem ser exibidas como grupos estruturados, em vez de ficarem embutidas em um bloco único sem separação clara.
- A lógica deve preservar a associação entre cada tecnologia e a categoria correta, independentemente do idioma.

Requisitos funcionais:
4. Aplicar tradução automática das categorias de tecnologias conforme o idioma selecionado.
5. Garantir que a seção de tecnologias seja renderizada com agrupamento por categorias em português, quando o idioma de saída for português.
6. Garantir que a estrutura de categorias seja mantida mesmo quando os itens de tecnologia estejam em listas longas ou contenham termos técnicos diversos.
7. Evitar que categorias de tecnologia sejam descartadas ou convertidas em texto plano sem estrutura.

### 3. Consistência entre seleção de idioma e saída final

- O idioma escolhido para o currículo deve orientar tanto os rótulos quanto as categorias, sem depender de uma tradução parcial ou manual.
- O resultado final deve parecer coerente para o usuário, independentemente do canal de saída usado.

Requisitos funcionais:
8. Garantir que a escolha de idioma do currículo seja aplicada de forma uniforme durante a geração do conteúdo e da renderização final.
9. Manter a consistência entre o conteúdo textual gerado e a representação visual do currículo.
10. Permitir que futuras expansões para outros idiomas reutilizem a mesma estrutura de localização sem reescrever a lógica central.

## Experiência do Usuário

Personas:
- Candidato: deseja que seu currículo fique bem apresentado e em conformidade com o idioma desejado.
- Recrutador: precisa ler rapidamente as competências técnicas do candidato sem se confundir com rótulos inconsistentes.
- Desenvolvedor de produto: precisa de uma solução confiável e reutilizável para manter a qualidade da geração do currículo.

Jornada principal:
- O usuário seleciona um idioma para o currículo.
- O sistema gera ou adapta o conteúdo do currículo.
- O sistema apresenta as seções e as categorias de tecnologia no idioma correto.
- O usuário visualiza o currículo e identifica rapidamente suas competências técnicas e sua estrutura.

## Restrições Técnicas de Alto Nível

- A correção deve ser integrada ao fluxo atual de geração e adaptação de currículos, sem exigir uma reestruturação completa do modelo de dados.
- A solução deve preservar as informações já existentes no currículo e não introduzir novas tecnologias, experiências ou competências inventadas.
- A implementação deve ser compatível com o mecanismo de geração atual utilizado para o PDF e para o conteúdo textual.
- A lógica de localização deve ser reutilizável e não pode depender de regras hard-coded dispersas pelo código.

## Fora de Escopo

- Redesenhar completamente o layout do currículo.
- Criar um novo mecanismo de geração de currículos fora do fluxo atual.
- Alterar o conteúdo factual do currículo para incluir ou remover competências técnicas.
- Implementar suporte a idiomas adicionais além do português e do inglês neste escopo inicial.

## Questões em Aberto

- A correção deve cobrir apenas português e inglês ou também servir de base para outros idiomas no futuro?
- A estrutura de categorias de tecnologia deve ser fixa para os idiomas suportados, ou deve ser possível configurá-la por locale?
- O comportamento padrão, em caso de idioma não mapeado, deve ser usar o idioma original do currículo ou o idioma selecionado com fallback parcial?

# Documento de Requisitos de Produto (PRD) — JOB-0034

## Visão Geral

Com a JOB-0033, o usuário passa a revisar o currículo adaptado antes do PDF. A IA, porém, só atua uma vez: na adaptação inicial, para todas as seções de uma vez. Se o usuário não gostar do texto de uma seção, ou se editar um trecho e quiser que a IA o refine, a única opção é reescrever à mão ou refazer a adaptação inteira.

Este PRD adiciona um botão **"Sugestões de IA"** em cada seção e em cada experiência. O botão pede à IA uma nova versão só daquele trecho, a partir do texto atual do campo. A IA devolve uma **sugestão**, que o usuário aplica ou descarta. Nada é trocado sem a decisão do usuário.

O mesmo conceito vale para a tela "Meu perfil". Lá não existe vaga-alvo, então a sugestão foca na qualidade da escrita (clareza, verbos de ação, resultados), sem adaptar para uma vaga.

Analogia: funciona como o "sugerir alteração" de um editor de documentos. A IA propõe; o usuário aceita ou recusa, trecho por trecho.

## Objetivos

- Permitir refinamento pontual pela IA, sem refazer a adaptação inteira.
- Dar ao usuário controle total: nenhuma sugestão substitui texto sem confirmação.
- Melhorar a qualidade do currículo mestre na tela "Meu perfil".
- Reaproveitar a mesma interação nas duas telas (DRY).

Como medir o sucesso:

- Proporção de sugestões aplicadas sobre sugestões pedidas (indicador de utilidade).
- Redução de adaptações completas refeitas para a mesma vaga.
- Nenhuma sugestão aplicada sem ação explícita do usuário.

## Histórias de Usuário

Persona principal: **candidato** que revisa o currículo adaptado (JOB-0033) ou mantém o currículo mestre.

1. Como candidato na revisão, eu quero pedir à IA uma nova versão só do resumo profissional, para melhorar esse trecho sem perder as edições das outras seções.
2. Como candidato na revisão, eu quero pedir uma sugestão para uma experiência específica, para alinhá-la melhor à vaga.
3. Como candidato na revisão, eu quero pedir uma sugestão para a seção de tecnologias, para destacar as que a vaga pede e que eu já informei.
4. Como candidato, eu quero ver a sugestão ao lado do texto atual antes de aplicar, para decidir com segurança.
5. Como candidato, eu quero que a IA parta do texto que eu já editei, e não do original, para não perder minhas correções.
6. Como candidato em "Meu perfil", eu quero sugestões para o resumo e para cada experiência, para melhorar a escrita do meu currículo mestre.
7. Como candidato, eu quero continuar editando outras seções enquanto a IA responde, para não ficar parado esperando.

Casos extremos:

- Campo vazio: o botão fica desabilitado, com a dica "Preencha o texto para pedir sugestões".
- A IA falha ou demora demais: o texto atual fica intacto e aparece uma mensagem de erro no próprio bloco.
- O usuário edita o campo enquanto a sugestão está pendente: a sugestão, ao chegar, continua sendo só uma proposta; o texto editado não é sobrescrito.
- O usuário pede nova sugestão para o mesmo campo: a anterior é substituída pela nova.

## Funcionalidades Principais

### 1. Sugestão de IA na tela de revisão (contexto da vaga)

Cada bloco elegível da revisão tem o botão "Sugestões de IA". A IA usa a vaga e o idioma alvo da adaptação.

Requisitos funcionais:

1. A tela de revisão deve exibir o botão "Sugestões de IA" no resumo profissional, na seção de tecnologias e em cada experiência estruturada.
2. Quando a fonte for um PDF da biblioteca, o bloco de texto de experiências deve ter o botão.
3. Formação, certificações e idiomas não devem ter o botão nesta versão.
4. A sugestão deve considerar a descrição da vaga, os requisitos já analisados e o idioma alvo da adaptação.
5. A sugestão de uma experiência deve alterar apenas a descrição. Cargo, empresa e período devem ser preservados.
6. A sugestão não deve inventar fatos, tecnologias, resultados ou métricas que não estejam no texto enviado ou no restante do currículo.

### 2. Sugestão de IA na tela "Meu perfil" (sem vaga)

Requisitos funcionais:

7. A tela "Meu perfil" deve exibir o botão "Sugestões de IA" no resumo profissional e em cada experiência.
8. A sugestão deve melhorar clareza, objetividade e uso de verbos de ação, mantendo o idioma do texto enviado.
9. A sugestão não deve inventar fatos, tecnologias, resultados ou métricas.
10. Aplicar uma sugestão não deve salvar o perfil. O usuário continua precisando clicar em "Salvar perfil".

### 3. Interação comum (as duas telas)

Requisitos funcionais:

11. A IA deve receber o texto atual do campo, incluindo edições manuais ainda não salvas ou confirmadas.
12. A sugestão deve aparecer no próprio bloco, com o texto atual e o texto sugerido visíveis ao mesmo tempo.
13. O usuário deve poder aplicar ou descartar a sugestão.
14. Aplicar deve substituir apenas o campo daquele bloco e marcá-lo como alterado.
15. Enquanto a sugestão é gerada, o botão daquele bloco deve mostrar estado de carregamento. Os demais campos e botões devem continuar utilizáveis.
16. Em falha da IA, o sistema deve mostrar uma mensagem no bloco e manter o texto atual intacto.
17. O botão deve ficar desabilitado quando o campo estiver vazio.
18. Uma sugestão não deve alterar nenhum outro campo, seção ou experiência.

## Experiência do Usuário

Jornada na revisão:

1. O usuário está na tela de revisão (JOB-0033) e acha o resumo genérico.
2. Clica em "Sugestões de IA" no bloco "Dados pessoais", junto ao resumo.
3. O botão mostra "Gerando sugestão…". O usuário segue editando uma experiência.
4. A sugestão aparece abaixo do resumo, em destaque, com as ações "Aplicar" e "Descartar".
5. Ele aplica. O resumo muda e o rodapé mostra "Alterações não confirmadas".
6. Ao final, clica em "Confirmar e gerar PDF", como na JOB-0033.

Jornada em "Meu perfil": idêntica, mas sem vaga; o final é "Salvar perfil".

Requisitos de UI/UX:

- Botão com o mesmo rótulo e ícone nas duas telas, posicionado junto ao campo de texto do bloco (como nas referências de mercado enviadas).
- Sugestão em área visualmente distinta (fundo de destaque), identificada como "Sugestão da IA".
- Mensagem de espera coerente com as demais ações de IA do sistema.

Acessibilidade:

- A chegada da sugestão deve ser anunciada a leitores de tela (`aria-live="polite"`).
- Os botões "Aplicar" e "Descartar" devem ter rótulos que indiquem o bloco (ex.: "Aplicar sugestão na experiência 2").
- Após aplicar ou descartar, o foco deve voltar ao campo de texto do bloco.

## Restrições Técnicas de Alto Nível

- Depende da JOB-0033 (tela de revisão, rascunho no frontend e componentes de formulário compartilhados).
- Arquitetura hexagonal: as sugestões entram por portas de IA; a tela não conhece o provedor.
- Reaproveitar as capacidades de ajuste de seção e de experiência já usadas na adaptação.
- Nada é persistido no servidor: a sugestão é uma resposta pontual.
- Evitar chamadas de IA repetidas para analisar a mesma vaga a cada sugestão.
- Dados pessoais e textos do currículo não devem aparecer em logs.
- Indisponibilidade da IA deve seguir o padrão atual do sistema (erro de provedor indisponível).

## Fora de Escopo

- Editor com formatação (negrito, itálico, listas pela barra de ferramentas). O campo segue como texto simples.
- Sugestões para formação, certificações, idiomas e dados de contato.
- Sugestões para a lista de tecnologias da tela "Meu perfil".
- Várias sugestões alternativas para o mesmo campo ao mesmo tempo.
- Comparação palavra a palavra (diff destacado) entre texto atual e sugestão.
- Histórico de sugestões ou desfazer em vários níveis.
- Sugestão de IA com uma vaga-alvo dentro da tela "Meu perfil".
- Limite de uso ou cobrança por sugestão.

## Questões em Aberto

1. Deve haver um "Desfazer" logo após aplicar uma sugestão? Hoje a proposta é decidir antes de aplicar.
2. A sugestão de tecnologias na revisão deve poder incluir tecnologias da vaga que não estão no currículo? O ajuste atual da adaptação faz isso para fins de ATS, o que conflita com a regra "não inventar fatos" (RF6).
3. Vale incluir uma instrução livre do usuário (ex.: "deixe mais curto") junto ao pedido de sugestão?
4. Precisamos de um limite de sugestões por minuto para controlar custo de IA?

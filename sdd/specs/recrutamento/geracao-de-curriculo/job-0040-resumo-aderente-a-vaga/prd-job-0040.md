# Documento de Requisitos de Produto (PRD) — JOB-0040

## Visão Geral

Hoje a IA reescreve o resumo (seção Perfil) pedindo apenas para "enfatizar a experiência e competências mais alinhadas à vaga". O resultado tende a ser genérico: ou repete frases da vaga, ou ignora o que a vaga pede no dia a dia.

Este PRD define como o resumo passa a refletir o que a vaga exige, de forma natural e curta, sem copiar o texto da vaga.

Exemplos do comportamento esperado:

- Vaga de Engenheiro de Software que pede arquitetura hexagonal e code review: o resumo cita essas práticas dentro de uma frase sobre como o candidato trabalha, sem listar os termos como requisitos.
- Vaga de Forward Deployed Engineer (FDE), que não detalha tudo no texto: o resumo usa o título da vaga e o senso comum do cargo (atuação junto ao cliente, integração de sistemas, prototipação rápida, comunicação técnica) quando o histórico do candidato sustenta isso.

Analogia: hoje o resumo é um espelho da vaga. Com a mudança, ele é a apresentação de uma pessoa que já conhece o trabalho que a vaga descreve.

Depende da JOB-0037 (regra de responsabilidades implícitas e foco de refino), já integrada.

### Resultado da primeira avaliação manual (vaga FDE Sênior)

A primeira versão da regra (até 3 frases, sem copiar) não atendeu ao objetivo:

- **Tamanho:** o resumo passou de 200 palavras. O limite de 3 frases foi cumprido com frases enormes e listas.
- **Cópia:** listas inteiras da vaga foram reproduzidas ("ferramentas e dados, permissões, limites de atuação, avaliações, qualidade, confiabilidade, custo, latência...").
- **Fidelidade:** o texto citou temas (RAG, MCP, orquestração de agentes) sem base visível no perfil.
- **Voz:** a frase "Para esta oportunidade, os temas técnicos relevantes incluem..." fala da vaga, não do candidato.
- **Título:** o resumo abriu com o título do perfil ("Engenheiro de software") e ignorou o cargo-alvo.

Esta revisão do PRD fecha esses pontos com limites objetivos. A cobertura de temas que o perfil não sustenta fica para a JOB-0042 (banco de conquistas) e a JOB-0043 (perguntas de elucidação), que dão ao usuário um caminho explícito para afirmar essa experiência.

## Objetivos

- O resumo adaptado se apresenta na linha do cargo-alvo e menciona os temas centrais da vaga que o histórico sustenta.
- O resumo não reproduz trechos da vaga nem listas de termos dela.
- O resumo é curto (até 60 palavras) e verdadeiro em relação ao perfil do candidato.

Como medir o sucesso:

- Em um conjunto de vagas de teste (ao menos uma de engenharia de software, uma de Forward Deployed Engineer com lista longa de requisitos e uma de cargo fora de TI), a revisão manual confirma: até 60 palavras, sem cópia de trechos, sem lista de termos e com o cargo-alvo refletido.
- Nenhum resumo gerado traz anos de experiência, cargos, tecnologias ou práticas que o perfil não sustenta.
- Nenhuma regressão nos testes das JOB-0034 e JOB-0037.

## Histórias de Usuário

Persona principal: **candidato** que adapta o currículo para uma vaga.

1. Como candidato, eu quero que o resumo fale dos temas que a vaga valoriza (ex.: arquitetura hexagonal, code review), para que o recrutador veja a ligação com a vaga já nas primeiras linhas.
2. Como candidato, eu quero que o resumo não repita as frases da vaga, para que o texto soe como meu e não como cópia.
3. Como candidato, eu quero que o resumo use o que é comum ao cargo da vaga, mesmo quando a vaga não detalha, para cobrir o que o recrutador espera ver.
4. Como candidato, eu quero que o resumo seja curto, para que caiba no topo da página como no meu modelo atual.
5. Como candidato, eu quero que o resumo não afirme o que meu histórico não sustenta, para que eu consiga defendê-lo em entrevista.
6. Como candidato, eu quero que o título da vaga oriente o resumo, para que ele fale a língua da posição.

Casos extremos:

- Vaga com descrição curta ou vazia: usar apenas o título da vaga (cargo-alvo) e o senso comum do cargo.
- Vaga com listas longas de requisitos: o resumo escolhe até 3 temas e descarta o resto.
- Vaga que pede algo sem relação com o histórico (ex.: gestão de pessoas para quem nunca gerenciou): o resumo não cita.
- Vaga em idioma diferente do currículo: o resumo segue o idioma alvo escolhido, não o da vaga.
- Perfil sem resumo original: a IA monta o resumo a partir das experiências e tecnologias do perfil.

## Funcionalidades Principais

### 1. Resumo orientado pelo cargo e pelos temas da vaga

Requisitos funcionais:

1. O resumo adaptado deve refletir os temas centrais da vaga (práticas, tipo de atuação, contexto do cargo) que o histórico do candidato sustenta.
2. O título da vaga (cargo-alvo) deve ser o eixo do resumo: o texto descreve o candidato na linha desse cargo, com a atuação típica dele que o histórico sustenta. O resumo não declara como título um cargo que o candidato não exerceu.
3. O resumo não deve copiar trechos da vaga. Os temas entram em frases próprias, de forma natural.
4. O resumo deve ter no máximo 60 palavras, em um único parágrafo de até 3 frases. O limite de palavras é obrigatório.
5. O resumo não deve conter listas de termos, nem ponto e vírgula, e deve citar no máximo 3 temas da vaga, escritos como ações do candidato e não como substantivos soltos.
6. O resumo não deve falar da vaga nem da oportunidade (ex.: "para esta vaga", "os temas relevantes incluem"). Ele fala do candidato.
7. O resumo não deve inventar anos de experiência, cargos, empresas, tecnologias, práticas nem métricas. Tema sem sustentação no histórico é omitido.
8. O resumo mantém a voz do resumo original do perfil.
9. A regra vale para o resumo gerado na adaptação e para o botão "Sugestões de IA" do resumo na revisão (qualquer foco, inclusive "palavras-chave", sem copiar trechos da vaga).
10. A regra vale para qualquer fonte do currículo (Meu perfil ou PDF salvo).

## Experiência do Usuário

Nenhuma tela nova. O usuário continua gerando o currículo adaptado e revisando o resumo na tela de revisão, onde já pode editá-lo e pedir sugestões de IA.

- O aviso de revisão existente ("Confirme que você consegue defender em entrevista o que a IA ajustou") passa a cobrir também o resumo. Nenhuma mudança de texto é obrigatória.
- Acessibilidade: sem mudança.

## Restrições Técnicas de Alto Nível

- Usar o provedor de IA e o fluxo de adaptação existentes, sem novo serviço externo.
- Não aumentar de forma relevante o tempo de geração do currículo (o aviso atual é de até 1 minuto).
- Privacidade: a descrição da vaga e o perfil seguem sendo enviados ao provedor de IA como hoje.

## Fora de Escopo

- Alterar o formato, o layout ou o limite de caracteres do PDF.
- Mudar as experiências e a seção de tecnologias (cobertas pelas JOB-0037 e JOB-0041).
- Validação automática em tempo de execução de cópia da vaga (a garantia vem das instruções à IA e da revisão do usuário).
- Perguntas de elucidação ao usuário e banco de conquistas (JOB-0042 e JOB-0043).
- Resumo em mais de um idioma ao mesmo tempo.

## Questões em Aberto

1. Resolvida: o tamanho máximo é de 60 palavras, como limite obrigatório.
2. Resolvida: o resumo cita só o que o histórico sustenta. Para afirmar atuação que o perfil não mostra, o usuário usa o banco de conquistas (JOB-0042) e as perguntas de elucidação (JOB-0043).
3. Como medir "não copiar a vaga"? A proposta é revisão manual no conjunto de vagas de teste; um verificador automático (tamanho e sobreposição com a vaga) seria um item futuro, a reabrir se a avaliação manual ainda mostrar cópia.
4. O limite de 60 palavras e "até 3 temas" cortam conteúdo útil em perfis longos? Avaliar na revisão manual.

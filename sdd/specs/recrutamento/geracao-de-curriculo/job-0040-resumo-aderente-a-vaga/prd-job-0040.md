# Documento de Requisitos de Produto (PRD) — JOB-0040

## Visão Geral

Hoje a IA reescreve o resumo (seção Perfil) pedindo apenas para "enfatizar a experiência e competências mais alinhadas à vaga". O resultado tende a ser genérico: ou repete frases da vaga, ou ignora o que a vaga pede no dia a dia.

Este PRD define como o resumo passa a refletir o que a vaga exige, de forma natural e curta, sem copiar o texto da vaga.

Exemplos do comportamento esperado:

- Vaga de Engenheiro de Software que pede arquitetura hexagonal e code review: o resumo cita essas práticas dentro de uma frase sobre como o candidato trabalha, sem listar os termos como requisitos.
- Vaga de Forward Deployed Engineer, que não detalha tudo no texto: o resumo usa o senso comum do cargo (atuação junto ao cliente, integração de sistemas, prototipação rápida, comunicação técnica) quando isso é coerente com o histórico do candidato.

Analogia: hoje o resumo é um espelho da vaga. Com a mudança, ele é a apresentação de uma pessoa que já conhece o trabalho que a vaga descreve.

Depende da JOB-0037 (regra de responsabilidades implícitas e foco de refino), já integrada.

## Objetivos

- O resumo adaptado menciona os temas centrais da vaga, incluindo os que fazem parte do cargo mesmo sem estarem escritos.
- O resumo não reproduz trechos da vaga.
- O resumo continua curto e verdadeiro em relação ao perfil do candidato.

Como medir o sucesso:

- Em um conjunto de vagas de teste (ao menos uma de engenharia de software, uma de Forward Deployed Engineer e uma de cargo fora de TI), a revisão manual confirma que o resumo cobre os temas centrais e não copia a vaga.
- Nenhum resumo gerado traz anos de experiência, cargos ou tecnologias que o perfil não sustenta.
- Nenhuma regressão nos testes das JOB-0034 e JOB-0037.

## Histórias de Usuário

Persona principal: **candidato** que adapta o currículo para uma vaga.

1. Como candidato, eu quero que o resumo fale dos temas que a vaga valoriza (ex.: arquitetura hexagonal, code review), para que o recrutador veja a ligação com a vaga já nas primeiras linhas.
2. Como candidato, eu quero que o resumo não repita as frases da vaga, para que o texto soe como meu e não como cópia.
3. Como candidato, eu quero que o resumo use o que é comum ao cargo da vaga, mesmo quando a vaga não detalha, para cobrir o que o recrutador espera ver.
4. Como candidato, eu quero que o resumo seja curto, para que caiba no topo da página como no meu modelo atual.
5. Como candidato, eu quero que o resumo não afirme o que meu histórico não sustenta, para que eu consiga defendê-lo em entrevista.

Casos extremos:

- Vaga com descrição curta ou vazia: usar apenas o título da vaga (cargo-alvo) e o senso comum do cargo.
- Vaga que pede algo sem relação com o histórico (ex.: gestão de pessoas para quem nunca gerenciou): o resumo não cita.
- Vaga em idioma diferente do currículo: o resumo segue o idioma alvo escolhido, não o da vaga.
- Perfil sem resumo original: a IA monta o resumo a partir das experiências e tecnologias do perfil.

## Funcionalidades Principais

### 1. Resumo orientado pelo cargo e pelos temas da vaga

Requisitos funcionais:

1. O resumo adaptado deve refletir os temas centrais da vaga (práticas, tipo de atuação, contexto do cargo) que o histórico do candidato sustenta.
2. O resumo deve usar o título da vaga (cargo-alvo) e o senso comum do cargo para incluir o que a vaga não detalha, desde que seja típico do cargo e coerente com o histórico.
3. O resumo não deve copiar trechos da vaga. Os temas entram em frases próprias, de forma natural.
4. O resumo deve manter o tamanho de um parágrafo curto (proposta: até 3 frases ou 60 palavras; ver Questões em Aberto).
5. O resumo não deve inventar anos de experiência, cargos, empresas, tecnologias nem métricas.
6. A regra vale para o resumo gerado na adaptação e para o botão "Sugestões de IA" do resumo na revisão (foco "aderência à vaga").
7. A regra vale para qualquer fonte do currículo (Meu perfil ou PDF salvo).

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
- Resumo em mais de um idioma ao mesmo tempo.

## Questões em Aberto

1. Qual o tamanho máximo aceito para o resumo? O modelo de referência tem cerca de 45 palavras e 3 frases. A proposta é até 60 palavras.
2. Até onde vai o "senso comum do cargo" quando o histórico não cobre o tema? A proposta é citar só o que o candidato exerceu em algum cargo anterior, como na regra da JOB-0037.
3. Como medir "não copiar a vaga"? A proposta é revisão manual no conjunto de vagas de teste; um verificador automático seria um item futuro.

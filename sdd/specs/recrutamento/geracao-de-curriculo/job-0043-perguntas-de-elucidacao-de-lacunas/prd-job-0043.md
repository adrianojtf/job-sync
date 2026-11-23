# Documento de Requisitos de Produto (PRD) — JOB-0043

## Visão Geral

Quando uma vaga pede algo que o perfil do candidato não mostra, a IA tem duas opções ruins: omitir o tema e perder aderência, ou citar o tema sem base e criar risco para o candidato. Muitas vezes o candidato viveu aquilo e simplesmente nunca escreveu no perfil. Exemplo: a vaga de Forward Deployed Engineer pede atuação junto a clientes e construção de MVPs, e o candidato fez isso em um projeto que o perfil não detalha.

Este PRD define **perguntas de elucidação**: antes de gerar o currículo, o sistema compara a vaga com o perfil, identifica as lacunas e pergunta ao candidato se ele viveu aquilo. Se a resposta for "sim", o candidato aponta a experiência e descreve um caso. O sistema transforma o caso em uma conquista, o candidato a aprova, e ela entra no banco de conquistas (JOB-0042). O resumo e as experiências do currículo passam a usar esse fato confirmado.

Analogia: em vez de a IA preencher o formulário e pedir que o candidato confira depois, ela age como um recrutador numa entrevista. Pergunta primeiro e escreve depois.

Depende da JOB-0042 (banco de conquistas) e da JOB-0040 (resumo aderente à vaga).

## Objetivos

- O candidato afirma, de forma explícita e antes da geração, a experiência que o perfil não mostra.
- Cada afirmação nova vira uma conquista aprovada, ligada a uma experiência e guardada no banco.
- O resumo e as experiências usam o que o perfil sustenta e o que o candidato confirmou, sem inventar o resto.
- A etapa de perguntas é curta e pode ser pulada.

Como medir o sucesso:

- Em uma avaliação manual com ao menos duas vagas (uma de Forward Deployed Engineer e uma de engenharia de software) e um perfil com lacunas, as perguntas cobrem os temas centrais ausentes do perfil e não repetem o que o perfil já mostra.
- Nenhuma frase do resumo ou das conquistas cita tema que o perfil não sustenta e que o candidato não confirmou.
- Todo resumo ou conquista com tema vindo de uma resposta tem uma conquista aprovada no banco.
- Nenhuma regressão nos testes das JOB-0035, JOB-0037, JOB-0040 e JOB-0042.

## Histórias de Usuário

Persona principal: **candidato** que adapta o currículo para uma vaga cujos temas o perfil só cobre em parte.

1. Como candidato, eu quero que o sistema me pergunte pelos temas da vaga que meu perfil não mostra, para eu afirmar o que realmente vivi.
2. Como candidato, eu quero apontar em qual experiência vivi aquilo, para o fato ficar no lugar certo do meu histórico.
3. Como candidato, eu quero descrever um caso e revisar a conquista escrita pela IA antes de salvá-la, para o texto ser fiel ao que fiz.
4. Como candidato, eu quero responder "não" ou pular uma pergunta, para o currículo não afirmar o que não vivi.
5. Como candidato, eu quero que a conquista fique guardada, para não responder a mesma pergunta em outra vaga.
6. Como candidato, eu quero poder pular todas as perguntas e gerar o currículo, para ganhar tempo quando já estou satisfeito com o perfil.

Casos extremos:

- O perfil já sustenta todos os temas da vaga: a etapa de perguntas não aparece.
- A vaga tem muitos temas ausentes: o sistema pergunta só pelos mais centrais, no máximo 5 perguntas.
- O candidato responde "sim", mas não aponta uma experiência: a conquista não é criada, e o tema não entra no currículo.
- A conquista descrita se parece com uma já guardada: o aviso de duplicidade da JOB-0042 aparece.
- O candidato responde "não": o tema não entra no currículo.
- Perfil sem experiências cadastradas: a etapa não se aplica, e o comportamento atual continua.
- Currículo vindo de PDF salvo (sem experiências estruturadas): a etapa não se aplica.

## Funcionalidades Principais

### 1. Identificação de lacunas

Requisitos funcionais:

1. Antes da geração, o sistema deve extrair os temas centrais da vaga e do cargo-alvo (título da vaga) e compará-los com o perfil, incluindo o banco de conquistas.
2. Um tema é uma lacuna quando o perfil e o banco não o sustentam.
3. O sistema deve ordenar as lacunas pela centralidade na vaga e perguntar por no máximo 5.
4. Temas já sustentados pelo perfil não geram pergunta.

### 2. Perguntas de elucidação

Requisitos funcionais:

5. Cada lacuna vira uma pergunta objetiva em linguagem direta (ex.: "Você já desenvolveu um sistema do zero em colaboração com um cliente?").
6. As respostas possíveis são "Sim", "Não" e "Prefiro não responder".
7. Em "Sim", o candidato deve escolher a experiência em que viveu aquilo e descrever um caso (o que fez, para quem e o resultado, se houver).
8. A IA deve redigir uma conquista a partir do caso, sem acrescentar fato, número ou resultado que o candidato não informou.
9. O candidato deve revisar e poder editar a conquista antes de aprová-la. Só a conquista aprovada é salva.
10. A conquista aprovada deve ser salva no banco da experiência escolhida (JOB-0042), com origem "resposta às perguntas".
11. Em "Não" ou "Prefiro não responder", o tema não entra no currículo daquela geração.
12. O candidato deve poder pular toda a etapa e gerar o currículo com o perfil atual.

### 3. Uso das respostas na geração

Requisitos funcionais:

13. O resumo (JOB-0040) e as experiências devem poder usar as conquistas aprovadas na etapa, com as mesmas regras de fidelidade e limite de tamanho.
14. As conquistas aprovadas entram na seleção de 3 a 5 por experiência (JOB-0042), como as demais.
15. As conquistas aprovadas ficam disponíveis para as próximas vagas.

## Experiência do Usuário

Fluxo principal:

1. O usuário informa a vaga, o cargo e a empresa e pede o currículo adaptado.
2. O sistema mostra a etapa "Perguntas sobre a vaga", com as perguntas das lacunas, uma por vez ou em lista.
3. Em cada pergunta, o usuário escolhe "Sim", "Não" ou "Prefiro não responder". Em "Sim", escolhe a experiência e descreve o caso.
4. O usuário revisa a conquista redigida e a aprova ou edita.
5. O sistema gera o currículo adaptado, usando o perfil e as conquistas aprovadas.
6. Na revisão, o usuário edita o que quiser, como hoje, e gera o PDF.

Requisitos de UX:

- Um botão "Pular perguntas e gerar" sempre visível.
- O número de perguntas é informado antes de começar (ex.: "3 perguntas sobre a vaga").
- O aviso de revisão existente continua visível na tela final.
- Acessibilidade: perguntas, opções e campos acessíveis por teclado e leitor de tela.

## Restrições Técnicas de Alto Nível

- Usar o provedor de IA existente, sem novo serviço externo.
- A identificação de lacunas adiciona uma etapa antes da geração. Ela não deve atrasar de forma relevante o fluxo, e o usuário deve poder pular a etapa.
- Privacidade: a vaga, o perfil, as conquistas e as respostas são enviados ao provedor de IA como o restante do perfil.
- A responsabilidade pela veracidade da resposta é do usuário. O sistema registra a origem da conquista e mantém o aviso de revisão.

## Fora de Escopo

- Guardar respostas "Não" para não repetir a pergunta em outras vagas.
- Perguntas sobre fatos que não sejam experiência profissional (formação, idiomas, certificações).
- Validação externa da resposta do candidato.
- Cadastro manual de conquistas (JOB-0042).
- Mudar o formato ou o layout do PDF.

## Questões em Aberto

1. Perguntas por vez ou em lista? Decidir no desenho de UX, priorizando menos atrito.
2. Guardar "Não" para não repetir a pergunta em outra vaga evita atrito, mas pode esconder uma experiência que o candidato passou a ter. Decidir depois da primeira avaliação.
3. Como medir se uma lacuna está bem identificada? Proposta: revisão manual com vagas de teste, e um conjunto fixo de casos para evolução futura.
4. O candidato aponta uma experiência que, pelo cargo e pelo período, não combina com o caso. O sistema deve apenas aceitar, ou deve avisar? Proposta: apenas aceitar nesta versão, mantendo o aviso de revisão.
5. A latência da etapa de lacunas cabe no limite de 1 minuto do fluxo de geração? Medir na techspec.

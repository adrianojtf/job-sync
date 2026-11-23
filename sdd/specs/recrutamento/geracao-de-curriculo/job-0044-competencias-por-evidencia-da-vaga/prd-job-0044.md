# Documento de Requisitos de Produto (PRD) — JOB-0044

## Visão Geral

Hoje a seção de tecnologias do currículo adaptado vira uma lista enorme. O prompt de adaptação manda incluir, em todas as seções, "todas as tecnologias" da análise da vaga, "mesmo que não estejam no conteúdo original". A análise da vaga mistura tecnologias, ferramentas, habilidades, metodologias e domínios. O resultado, com uma vaga de agentes de IA, foi uma lista de cerca de 85 itens, com "aprovação humana", "serviços financeiros" e "tratamento de falhas" ao lado de Java e Postgres. Isso polui a leitura e afirma coisas que o candidato pode não ter.

Este PRD define a regra do que entra na seção, que passa a se chamar **Competências**:

- entra o que o perfil mostra, ordenado pela relevância à vaga;
- a tecnologia da vaga sem evidência não entra, e vira uma **lacuna**, que a JOB-0043 (perguntas de elucidação) poderá perguntar;
- conceitos, domínios e habilidades não entram na lista (cabem no resumo e nas experiências);
- a lista tem um teto, próximo ao do currículo de referência.

Analogia: hoje a lista é uma lista de compras da vaga. Passa a ser a prateleira do candidato, arrumada na ordem que a vaga valoriza.

Depende da JOB-0041 (competências em tags) e da JOB-0037 (tecnologias equivalentes). A JOB-0043 consome as lacunas, mas não é pré-requisito.

## Objetivos

- Competências lista só o que o candidato tem ou afirmou, sem conceitos nem domínios da vaga.
- A lista cabe em cerca de 45 itens e começa pelo que a vaga mais pede.
- As tecnologias que a vaga pede e o candidato não mostra ficam visíveis como lacunas, em vez de entrar sem base.
- O resumo e as experiências deixam de ser obrigados a citar todas as tecnologias da vaga (coerente com a JOB-0040).

Como medir o sucesso:

- Com a vaga de agentes de IA citada acima e um perfil real, a lista final não tem conceito, domínio nem habilidade, e nenhuma tecnologia que o perfil e as experiências não sustentem.
- A lista tem no máximo 45 itens.
- Toda tecnologia da vaga que ficou de fora aparece na lista de lacunas.
- Nenhuma regressão nos testes das JOB-0037, JOB-0040 e JOB-0041.

## Histórias de Usuário

Persona principal: **candidato** que adapta o currículo para uma vaga.

1. Como candidato, eu quero que Competências traga só o que eu realmente uso, para o currículo ser verdadeiro e fácil de ler.
2. Como candidato, eu quero as tecnologias mais pedidas pela vaga no começo da lista, para o recrutador e o ATS as verem primeiro.
3. Como candidato, eu quero ver quais tecnologias da vaga ficaram de fora por falta de evidência, para eu decidir se as adiciono ou se respondo a pergunta de elucidação.
4. Como candidato, eu quero poder digitar uma tag a mais no editor, para incluir uma tecnologia que eu tenho e o perfil não mostra.
5. Como candidato, eu quero a seção chamada "Competências", para o título combinar com o meu modelo.

Casos extremos:

- A vaga não cita nenhuma tecnologia que o perfil não tenha: não há lacunas.
- O perfil tem mais de 45 itens: ficam os mais relevantes à vaga, e a ordem original dos demais é mantida.
- A tecnologia da vaga aparece só no texto de uma experiência: tem evidência e entra.
- A tecnologia da vaga é equivalente a uma do perfil (JOB-0037): entra, como hoje.
- A fonte é um PDF: os itens do PDF são o que o candidato tem.
- A vaga é em inglês e o currículo em português (ou o contrário): a comparação ignora maiúsculas e minúsculas e só considera o nome da tecnologia.

## Funcionalidades Principais

### 1. O que entra em Competências

Requisitos funcionais:

1. Entram: as tecnologias, ferramentas e práticas que o perfil lista; as tecnologias que a vaga pede e que as experiências do candidato citam; e as equivalências aplicadas pela JOB-0037.
2. Não entram: tecnologias ou ferramentas da vaga sem evidência (viram lacunas) e requisitos que a análise da vaga não classifica como tecnologia ou ferramenta (conceitos, domínios, habilidades).
3. A IA agrupa os itens permitidos em categorias e ordena pela relevância à vaga. Ela não pode acrescentar item fora do conjunto permitido; o sistema descarta qualquer item acrescentado.
4. A lista tem no máximo 45 itens. Ao passar disso, saem primeiro os que a vaga não pede.
5. Práticas de engenharia (ex.: Spec-Driven Development, Code Review) só entram se o perfil as lista.

### 2. Lacunas de tecnologia

6. O sistema deve calcular as tecnologias e ferramentas da vaga sem evidência e devolvê-las com o rascunho.
7. A revisão deve mostrar essas lacunas em um aviso, com a orientação de adicionar a tag se o candidato tem a tecnologia.
8. As lacunas ficam disponíveis para a JOB-0043 transformar em perguntas. Esta entrega não cria as perguntas.

### 3. Nome da seção e instruções de IA

9. A seção chama-se "Competências" no currículo em português e "Skills" no currículo em inglês, na tela e no PDF.
10. A instrução de IA que manda incluir "todas as tecnologias da análise de vaga" sai de todas as seções. Cada seção segue a sua própria regra.

## Experiência do Usuário

Na revisão, o bloco "Competências" mostra as categorias e tags, como na JOB-0041. Abaixo, quando houver lacunas, aparece um aviso: "Tecnologias da vaga que seu perfil não mostra: Kafka, RabbitMQ. Se você as usa, adicione a tag." O restante da revisão não muda.

- Acessibilidade: o aviso usa o mesmo componente de aviso da revisão, legível por leitor de tela.

## Restrições Técnicas de Alto Nível

- A decisão do que entra é determinística e testável. A IA agrupa e ordena; não decide o que o candidato tem.
- Usar o provedor de IA e o fluxo de adaptação existentes, sem novo serviço externo.
- O fluxo de geração não deve ficar mais lento de forma perceptível.

## Fora de Escopo

- As perguntas de elucidação (JOB-0043), inclusive guardar a resposta "Sim" no perfil.
- Sugestões da vaga com aceite em um clique na tela.
- Mudar o layout do PDF (coluna de rótulos).
- Mudar o que a IA faz nas experiências além de retirar a obrigação de citar todas as tecnologias da vaga.
- Corrigir a classificação da análise da vaga (tecnologia, ferramenta, habilidade etc.).

## Questões em Aberto

1. **Título em inglês.** A pesquisa feita para esta decisão aponta "Skills" como o título mais seguro; "Technical Skills" é aceito quando a lista é de ferramentas, e "Core Competencies" é mais amplo. Não encontrei teste de leitura por ATS que comprove diferença, só recomendações de blogs de carreira. A proposta é "Skills". Fontes: [Toptal](https://www.toptal.com/resume/career-center/skills-to-put-on-a-resume-a-complete-guide), [Enhancv](https://enhancv.com/blog/resume-headings/), [Jobscan](https://www.jobscan.co/blog/resume-examples-keywords-for-software-engineers/).
2. **O teto de 45 itens** vem do currículo de referência (cerca de 48). Ajustar depois de uma avaliação manual.
3. **Qualidade da classificação da análise da vaga.** Se ela marcar conceito como tecnologia, esse conceito vira lacuna. Medir na avaliação manual.
4. **Como a JOB-0043 divide o teto de 5 perguntas** entre temas e tecnologias. Decisão da JOB-0043; a proposta é um teto único, ordenado pela centralidade na vaga.
5. **Evidência por texto.** A busca do nome da tecnologia nas experiências ignora sinônimos (ex.: "Postgres" e "PostgreSQL"). Aceitar nesta versão, ou manter uma lista de sinônimos?

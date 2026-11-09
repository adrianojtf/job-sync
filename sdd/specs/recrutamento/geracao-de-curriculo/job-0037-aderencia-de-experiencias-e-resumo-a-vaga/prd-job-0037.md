# Documento de Requisitos de Produto (PRD) — JOB-0037

## Visão Geral

Hoje a IA adapta o resumo e cada experiência do currículo à vaga, mas de forma conservadora. Três problemas aparecem no uso:

1. **Tecnologia equivalente não aparece.** Se a vaga pede Java + Angular e o candidato trabalhou com Java + React, o currículo continua só com React. O prompt atual proíbe "inventar tecnologias". Com desenvolvimento apoiado por IA e SDD, a troca entre frameworks equivalentes deixou de ser uma barreira real, mas o ATS e o recrutador ainda filtram pela palavra exata.
2. **Responsabilidades implícitas ficam de fora.** Se a vaga é de Code Reviewer, e o candidato faz code review como parte do cargo, mas não escreveu isso no perfil, o currículo não cita a atividade. A IA também não recebe o título da vaga (cargo-alvo), embora ele já seja informado pelo usuário.
3. **"Sugestões de IA" repete a mesma abordagem.** Na revisão do currículo adaptado e em "Meu perfil", pedir uma nova sugestão para um texto já melhorado devolve algo muito parecido. Na revisão, o resumo usa o mesmo prompt da geração inicial, que trata o texto atual como "conteúdo original".

Este PRD define como o resumo e as experiências passam a refletir a vaga, e como o botão "Sugestões de IA" passa a refinar o texto atual com um foco diferente a cada pedido.

Analogia: hoje a IA age como um revisor de texto. Com esta mudança, ela age como um consultor de carreira que conhece a vaga, sabe quais tecnologias são equivalentes, lembra o que o cargo exige no dia a dia e, quando pedem outra versão, muda de ângulo em vez de repetir a mesma.

Depende da JOB-0034 (sugestões de IA por seção) e da JOB-0035 (conquistas e contexto nas experiências), já integradas.

## Objetivos

- O currículo adaptado cita as tecnologias pedidas pela vaga sempre que o candidato tem uma equivalente.
- O currículo cita as responsabilidades essenciais da vaga que são implícitas ao cargo que o candidato exerceu.
- O cargo-alvo orienta a ênfase e o vocabulário do resumo e das experiências.
- Cada novo pedido de sugestão parte do texto atual e traz uma abordagem diferente das anteriores.
- O usuário vê o que a IA trocou e pode desfazer na revisão.

Como medir o sucesso:

- Em vagas com tecnologia equivalente à do perfil, o score ATS da seção de experiências sobe em relação à versão sem troca (comparar antes e depois em um conjunto de vagas de teste).
- Em pedidos seguidos de sugestão para o mesmo campo, nenhuma sugestão é idêntica a uma anterior.
- Nenhuma regressão nos testes da JOB-0034 e da JOB-0035.

## Histórias de Usuário

Persona principal: **candidato** que adapta o currículo mestre para uma vaga e revisa o resultado.

1. Como candidato, eu quero que a IA troque uma tecnologia minha pela equivalente pedida na vaga, para passar no filtro do ATS.
2. Como candidato, eu quero que a troca não aconteça em todas as experiências, para que o histórico continue plausível e eu ainda mostre a tecnologia original.
3. Como candidato, eu quero que o contexto de cada experiência deixe explícito em qual tecnologia trabalhei (Angular no front-end, ou React no front-end), para o recrutador entender o cenário.
4. Como candidato, eu quero que a seção de tecnologias liste as duas (a original e a equivalente), para cobrir as duas palavras-chave.
5. Como candidato, eu quero que a IA cite responsabilidades que a vaga exige e que fazem parte do meu cargo (ex.: code review), mesmo que eu não as tenha escrito.
6. Como candidato, eu quero que o título da vaga oriente o resumo e as experiências, para que o currículo fale a língua da posição.
7. Como candidato, eu quero ver quais trocas de tecnologia a IA fez, para conferir antes de gerar o PDF.
8. Como candidato, eu quero clicar em "Sugestões de IA" várias vezes e receber, a cada vez, uma versão diferente que parte do texto atual.

Casos extremos:

- A tecnologia original aparece em só uma experiência: a troca acontece nela.
- A tecnologia equivalente já aparece em alguma experiência do perfil: não há troca, porque o candidato já tem a tecnologia.
- Não há equivalência na mesma categoria (ex.: vaga pede Kubernetes, o perfil tem React): não há troca.
- A experiência não tem descrição: não há troca nem responsabilidades novas (regra da JOB-0035 mantida).
- O usuário edita o campo entre dois pedidos de sugestão: o novo pedido parte do texto editado.
- Em "Meu perfil" não há vaga: os focos de refino não usam aderência nem palavras-chave da vaga.

## Funcionalidades Principais

### 1. Troca de tecnologias equivalentes

Requisitos funcionais:

1. A IA deve identificar, para cada tecnologia pedida pela vaga que não aparece no perfil, se o perfil tem uma tecnologia equivalente na mesma categoria (ex.: React ↔ Angular ↔ Vue; MySQL ↔ PostgreSQL; RabbitMQ ↔ Kafka).
2. A troca não deve acontecer entre categorias diferentes (ex.: framework de front-end por banco de dados).
3. Quando a tecnologia original aparece em uma só experiência, a troca deve ser feita nela.
4. Quando a tecnologia original aparece em duas ou mais experiências, ao menos uma delas deve manter a original. A troca deve ser feita nas mais recentes.
5. Na experiência com troca, o contexto deve citar a tecnologia nova de forma explícita (ex.: "usando Angular no front-end").
6. Na experiência que mantém a original, o contexto deve citar a original de forma explícita (ex.: "com React no front-end").
7. A seção de tecnologias deve listar a original e a equivalente.
8. O resumo pode citar a tecnologia equivalente, coerente com as experiências.

### 2. Responsabilidades implícitas ao cargo

Requisitos funcionais:

9. A IA deve receber o cargo-alvo (título da vaga) ao adaptar o resumo e as experiências e ao gerar sugestões na revisão.
10. A IA pode citar, em uma conquista ou no contexto, uma responsabilidade essencial da vaga que seja comum ao cargo que o candidato exerceu naquela experiência (ex.: code review para um desenvolvedor, gestão de backlog para um PO).
11. A IA não deve citar responsabilidades que não sejam típicas do cargo exercido (ex.: gestão de pessoas para um desenvolvedor júnior).
12. A IA não deve inventar métricas para uma responsabilidade implícita.
13. A regra deve ser genérica, sem lista fixa de cargos ou atividades.

### 3. Transparência na revisão

Requisitos funcionais:

14. A tela de revisão deve listar as trocas feitas: tecnologia original, tecnologia nova e experiência (cargo e empresa).
15. O aviso de revisão (da JOB-0035) deve passar a incluir trocas de tecnologia e responsabilidades implícitas: "Confirme que você consegue defender em entrevista o que a IA ajustou."
16. Sem trocas, a lista não aparece.

### 4. Sugestões de IA com refino variável

Requisitos funcionais:

17. O botão "Sugestões de IA" deve sempre partir do texto atual do campo, com as edições ainda não salvas.
18. Na revisão, a sugestão de qualquer seção (resumo, tecnologias, demais seções) deve usar um modo de refino, e não o modo de geração inicial.
19. Cada novo pedido para o mesmo campo deve usar um foco diferente do anterior, em rodízio:
    - Com vaga (revisão): aderência à vaga, impacto e resultados, palavras-chave da vaga, clareza e concisão.
    - Sem vaga (Meu perfil): impacto e resultados, clareza e concisão, ênfase técnica.
20. A IA deve receber as sugestões já mostradas para aquele campo (no máximo as 3 últimas) e não deve repeti-las.
21. O painel da sugestão deve mostrar o foco usado (ex.: "Foco: impacto e resultados").
22. O histórico de sugestões vale só enquanto a tela estiver aberta. Não é salvo.
23. As regras das funcionalidades 1 e 2 valem também para as sugestões da revisão. As trocas já feitas na experiência devem ser mantidas.

## Experiência do Usuário

Jornada na revisão:

1. O usuário informa a vaga, o cargo e a empresa e gera o currículo adaptado.
2. Na revisão, vê o aviso de conferência e a lista "Ajustes de tecnologia" (ex.: "React → Angular em Desenvolvedor Full Stack — Empresa X").
3. Lê as experiências: a mais recente cita Angular no contexto; a mais antiga cita React no contexto.
4. Clica em "Sugestões de IA" no resumo. Vê "Foco: aderência à vaga". Descarta.
5. Clica de novo. Vê "Foco: impacto e resultados", com outro texto. Aplica.
6. Gera o PDF.

Jornada em "Meu perfil": o usuário pede sugestões seguidas para uma experiência e recebe, a cada vez, uma versão com foco diferente, sem vaga.

Requisitos de UI/UX:

- A lista de ajustes de tecnologia fica logo abaixo do aviso, no topo da revisão.
- O foco aparece como subtítulo do painel "Sugestão da IA".
- O texto do botão não muda.

Acessibilidade:

- A lista de ajustes usa marcação de lista e um título.
- O foco faz parte do texto anunciado na região `aria-live` da sugestão.

## Restrições Técnicas de Alto Nível

- Arquitetura hexagonal: a regra de distribuição das trocas entre experiências é do domínio e deve ser determinística. A IA só aponta equivalências.
- Sem persistência nova: trocas e histórico de sugestões vivem na sessão da tela.
- A IA usa o provedor já configurado (OpenAI, via `ClienteOpenAI`).
- Dados pessoais e textos do currículo não aparecem em logs.
- Contratos de API: mudanças compatíveis (campos novos opcionais nos pedidos e campos novos nas respostas).
- Latência: no máximo uma chamada extra de IA por adaptação (identificar equivalências).

## Fora de Escopo

- Troca de tecnologias e distribuição entre experiências quando a fonte é um PDF (sem experiências estruturadas). Essa fonte recebe só o cargo-alvo e a regra de responsabilidades implícitas.
- Escolha manual da troca antes da geração (o usuário ajusta na revisão).
- Botão para desfazer uma troca de forma automática.
- Escolha manual do foco do refino.
- Salvar o histórico de sugestões.
- Alterar o currículo mestre ou a biblioteca de currículos.
- Troca de cargo, empresa ou período.

## Questões em Aberto

1. **Quantas experiências recebem a troca?** Proposta: com duas ou mais ocorrências, trocar em todas menos na mais antiga. Alternativa: trocar só na metade mais recente.
2. **Ordem das experiências:** a regra "mais recentes" assume a ordem do perfil (da mais recente para a mais antiga). Isso precisa ser confirmado no código do perfil estruturado.
3. **Lista de equivalências:** a IA decide a equivalência por categoria. Convém, em outra JOB, uma lista curada e editável pelo usuário?
4. **Responsabilidades implícitas na fonte PDF:** a regra entra só como instrução no prompt, sem garantia. Isso é aceitável?
5. **Foco no Meu perfil:** os três focos propostos (impacto, clareza, ênfase técnica) cobrem o uso esperado?

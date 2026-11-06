# Documento de Requisitos de Produto (PRD)

- **Código**: `JOB-0013`
- **Módulo**: `recrutamento`
- **Subsistema**: `analise-de-vagas`
- **Resumo da funcionalidade**: `avaliacao-vaga-experiencia-gpt-luna-jev`
- **Status**: Rascunho

## Visão Geral

Este PRD adiciona avaliações estruturadas para descrições de vagas e textos de experiências profissionais usando o Jev, da TypeSafe AI. O candidato poderá avaliar uma descrição de vaga isoladamente ou receber essa avaliação antes da adaptação do currículo. Também poderá avaliar uma experiência profissional sob demanda ou, quando a adaptação usar um perfil estruturado, receber uma avaliação de cada experiência após a adaptação. Todas as avaliações de experiência consideram uma vaga-alvo.

As avaliações devem apresentar um score e motivos escolhidos de categorias previamente definidas. O Jev foi anunciado como um modelo de decisões estruturadas, sem geração de texto livre; portanto, as explicações apresentadas ao usuário serão associadas às categorias do produto, não redigidas livremente pelo modelo.

Além disso, o modelo GPT Luna 6 substituirá o modelo Groq atualmente usado pelas operações de IA existentes no projeto. O Jev será usado especificamente para as novas avaliações e não substituirá o GPT Luna 6 nas demais operações.

## Objetivos

- Ajudar o candidato a identificar problemas de completude, clareza, relevância e inclusão em descrições de vagas.
- Ajudar o candidato a avaliar a qualidade do texto de suas experiências e sua aderência à vaga-alvo.
- Oferecer avaliações estruturadas, compreensíveis e não bloqueantes para apoiar a decisão do candidato.
- Migrar as operações de IA existentes que usam Groq para GPT Luna 6, preservando os fluxos e resultados funcionais já existentes.

## Histórias de Usuário

1. Como candidato, quero validar uma descrição de vaga antes de adaptar meu currículo, para entender sua qualidade e os pontos que merecem atenção.
2. Como candidato, quero solicitar a validação de uma vaga separadamente, para decidir se vale a pena prosseguir com aquela oportunidade.
3. Como candidato, quero avaliar uma experiência profissional em relação a uma vaga, para identificar oportunidades de melhorar sua clareza e relevância.
4. Como candidato, quero receber uma avaliação da experiência após a adaptação do currículo, para revisar o resultado sem tratar a avaliação como uma alteração automática.
5. Como usuário dos fluxos existentes, quero que as operações de IA continuem disponíveis após a migração para GPT Luna 6, sem precisar mudar minha forma de usá-las.

## Funcionalidades Principais

### 1. Validação de descrição de vaga com Jev

A avaliação considera completude, clareza, relevância e linguagem potencialmente enviesada ou excludente. Deve estar disponível como ação independente e também ocorrer antes da adaptação do currículo. A resposta não bloqueia a adaptação; ela apresenta um score e motivos associados a categorias fixas.

Requisitos funcionais:

1. O sistema deve permitir avaliar uma descrição de vaga sob demanda.
2. O sistema deve avaliar a descrição antes de iniciar a adaptação do currículo para a vaga.
3. A avaliação deve considerar completude, clareza, relevância para uma vaga e viés ou linguagem excludente.
4. O resultado deve conter um score de 0 a 100 e as categorias que justificam a avaliação.
5. Uma avaliação desfavorável não deve impedir o usuário de prosseguir com a adaptação.

### 2. Avaliação de experiência profissional com Jev

A avaliação considera clareza e escrita, qualidade e nível de detalhe, aderência à vaga-alvo e possíveis inconsistências ou exageros no texto. A avaliação deve estar disponível sob demanda e, para currículos originados de perfil estruturado, após a adaptação, uma vez para cada experiência. Ela não altera o currículo automaticamente nem verifica afirmações em fontes externas.

Requisitos funcionais:

6. O sistema deve permitir avaliar o texto de uma experiência profissional com uma vaga-alvo como contexto.
7. O sistema deve permitir solicitar essa avaliação sob demanda.
8. O sistema deve avaliar cada experiência após a adaptação quando o currículo tiver origem em um perfil estruturado.
9. O resultado deve conter um score de 0 a 100 e categorias relacionadas aos critérios avaliados.
10. A avaliação deve sinalizar possíveis inconsistências textuais sem afirmar que fatos foram verificados externamente e sem inventar informações.
11. O resultado da avaliação não deve alterar nem salvar automaticamente o texto da experiência.
12. Após adaptar um currículo originado de perfil estruturado, o sistema deve avaliar individualmente cada experiência profissional.

### 3. Migração das operações atuais para GPT Luna 6

Requisitos funcionais:

13. O sistema deve substituir o modelo Groq atualmente usado pelas operações de IA existentes no projeto por GPT Luna 6 (`gpt-6-luna`) pela API oficial da OpenAI.
14. Os fluxos existentes devem preservar seus contratos funcionais, sem exigir mudança na interação do usuário.
15. As avaliações novas de descrição de vaga e experiência devem continuar usando Jev, independentemente da migração dos demais fluxos.

## Experiência do Usuário

O candidato pode iniciar a avaliação de uma descrição de vaga como ação independente ou recebê-la automaticamente antes da adaptação do currículo. O resultado deve apresentar o score e as categorias identificadas, sem bloquear a continuação do fluxo.

Na avaliação de experiência, o usuário pode pedir uma análise sob demanda ou consultar o resultado gerado para cada experiência após adaptar um currículo de perfil estruturado. Para currículos enviados somente como PDF, a avaliação individual automática após adaptação não faz parte desta entrega. A avaliação é informativa: o usuário mantém controle sobre qualquer alteração do conteúdo.

As categorias e seus rótulos devem ser apresentados de forma clara. O score não deve ser comunicado como garantia de qualidade, adequação ou veracidade dos fatos.

## Restrições Técnicas de Alto Nível

- As avaliações estruturadas devem usar Jev, da TypeSafe AI, cuja saída é limitada a decisões estruturadas e não inclui geração livre de texto.
- As operações atuais de IA que usam Groq devem migrar para GPT Luna 6 (`gpt-6-luna`) pela API oficial da OpenAI.
- A primeira entrega disponibiliza as novas avaliações somente pela API FastAPI existente; não inclui alterações na interface Streamlit.
- O score agregado das avaliações deve ser apresentado na escala de 0 a 100.
- Descrições de vagas e dados de currículo podem conter dados pessoais e serão enviados a provedores externos de IA; o tratamento precisa respeitar as políticas de privacidade aplicáveis.
- A solução deve manter os limites entre domínio, camada de aplicação e adapters de infraestrutura definidos pelo projeto.
- Os identificadores de modelo, as credenciais e as falhas dos provedores devem ser tratados sem expor segredos ou detalhes internos ao usuário.

## Fora de Escopo

- Bloquear uma adaptação ou candidatura com base no score.
- Gerar explicações livres ou recomendações textuais usando Jev.
- Verificar a veracidade de experiências profissionais em fontes externas.
- Alterar ou salvar automaticamente o conteúdo do currículo a partir de uma avaliação.
- Avaliar automaticamente, experiência por experiência, currículos enviados somente como PDF após a adaptação.
- Redesenhar os fluxos existentes de extração, análise ATS, carta de apresentação ou descoberta de vagas, além da migração do modelo usada por eles.
- Definir uma política de retenção de dados dos provedores externos neste PRD.

## Questões em Aberto

1. Quais são os requisitos de retenção, uso e exclusão de dados enviados ao Jev e à API da OpenAI?

## Referências

- TypeSafe AI, “Introducing System One Models & Jev”: https://typesafe.ai/blog/introducing-system-one-models-and-jev
- TypeSafe AI, documentação de Jev: https://docs.typesafe.ai/
- OpenAI, modelo GPT-6 Luna: https://developers.openai.com/api/docs/models/gpt-6-luna

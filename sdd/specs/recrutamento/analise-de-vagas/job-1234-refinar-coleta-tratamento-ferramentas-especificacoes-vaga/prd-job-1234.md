# Documento de Requisitos de Produto (PRD)

## Visão Geral

O objetivo deste PRD é definir a correção e o refinamento do processo de coleta e tratamento de ferramentas, tecnologias e especificações extraídas de descrições de vagas. O problema identificado é que o sistema atualmente gera inferências imprecisas, como atribuir "Django" a uma vaga apenas por menção indireta de experiência em Python, quando esse framework não foi explicitamente listado.

## Objetivos

- Melhorar a precisão da extração de requisitos técnicos a partir de descrições de vagas.
- Evitar inferências indevidas de tecnologias que não são explicitamente mencionadas no texto da vaga.
- Preservar as informações explícitas da vaga enquanto reduz falsos positivos e ambiguidades.
- Aumentar a confiabilidade do processamento das vagas para suportar decisões de correspondência de candidatos e relatórios de skills.

## Histórias de Usuário

1. Como analista de talentos, eu quero que o sistema identifique apenas tecnologias e frameworks explicitamente mencionados na descrição da vaga para que eu possa confiar na lista de skills extraídas.
2. Como desenvolvedor do produto, eu quero que o motor de extração diferencie entre requisitos explícitos e inferências implícitas para reduzir ruído nas tags de tecnologia.
3. Como usuário de relatórios de vagas, eu quero que o sistema destaque quando um requisito técnico está implícito em vez de explícito, para poder revisar e validar casos ambíguos.

## Funcionalidades Principais

### 1. Refinamento da extração de ferramentas e tecnologias

- O sistema deve extrair e listar apenas tecnologias e frameworks explícitos mencionados no texto da vaga.
- O sistema deve marcar claramente as tecnologias inferidas como implícitas e não incluí-las no conjunto principal de requisitos técnicos sem revisão adicional.
- Caso uma tecnologia seja mencionada apenas em um contexto de experiência (por exemplo, "experiência em Python e desenvolvimento web"), não deve ser assumido automaticamente que frameworks específicos como Django estão presentes.

Requisitos funcionais:
1. Extrair todas as ferramentas, linguagens e frameworks explicitamente mencionados na vaga.
2. Identificar e classificar menções implícitas que dependem de contexto, sem promover essas inferências a requisitos explícitos.
3. Apresentar uma distinção clara entre requisitos explícitos e implícitos nos resultados de processamento.
4. Permitir revisão manual ou validação posterior de tecnologias classificadas como implícitas.

### 2. Tratamento de especificações da vaga

- O sistema deve analisar as seções de requisitos da vaga e separar: tecnologias, linguagens, frameworks, banco de dados, experiência desejada e habilidades comportamentais.
- O processamento deve considerar que termos como "Python" e "Django" têm relação, mas não devem ser equiparados automaticamente.
- A vaga de exemplo deve gerar "Python" e "Django" apenas quando "Django" estiver explicitamente presente.

Requisitos funcionais:
5. Extrair requisitos de banco de dados e outros sistemas mencionados (por exemplo, Oracle, MS SQL, MySQL) como categorias distintas.
6. Extrair níveis de experiência onde fornecidos (por exemplo, "1+ anos de experiência" e "avançado em inglês").
7. Reportar casos de ambiguidade ou inferência potencial para revisão humana.

### 3. Transparência e validação do resultado

- O sistema deve documentar a fonte de cada item extraído para facilitar auditoria.
- Os resultados devem indicar claramente quando um item foi inferido e qual texto de origem o gerou.

Requisitos funcionais:
8. Para cada tecnologia ou requisito extraído, incluir o trecho de texto original que motivou a extração.
9. Expor um indicador de confiança ou tipo de extração (explícito vs. implícito).
10. Permitir que um revisor aceite ou rejeite tecnologias inferidas antes de elas entrarem no conjunto final de skills.

## Experiência do Usuário

Personas:
- Analista de recrutamento: quer informação técnica confiável para selecionar candidatos.
- Equipe de produto/dados: quer métricas de precisão de extração e visibilidade sobre ambiguidade.
- Revisor de vagas: quer uma maneira de validar ou corrigir inferências automáticas.

Jornada e interações principais:
- O usuário insere ou recebe uma descrição de vaga.
- O sistema processa a vaga e extrai requisitos técnicos, destacando explicitamente o que foi mencionado e o que foi inferido.
- O usuário revisa itens marcados como implícitos e confirma ou ajusta o conjunto final de tecnologias.
- O sistema gera um resultado final limpo, que alimenta correspondência de candidatos e relatórios.

## Restrições Técnicas de Alto Nível

- A solução deve focar em refinamento da lógica de extração e classificação, sem alterar a aparência da interface do usuário.
- As regras de inferência devem ser revisáveis e configuráveis através do motor de processamento de texto.
- Não é necessário implementar uma nova interface de usuário para esta correção; a prioridade é a qualidade dos dados extraídos.
- A solução deve ser compatível com o formato de vagas já processado pela plataforma.

## Fora de Escopo

- Construir um sistema completo de recomendação de candidatos.
- Modificar o processo de coleta de vagas além da correção de extração de ferramentas e especificações.
- Adicionar suporte a processamento de linguagem natural avançado além do refinamento de regras e classificação de inferências para esta correção.
- Redesenhar a experiência do usuário final que consome os resultados de skills extraídos.

## Questões em Aberto

- Qual é o limite aceitável de tecnologias inferidas que podem ser exibidas sem revisão humana?
- Devemos considerar outras fontes de contexto além do texto da vaga (por exemplo, histórico de vagas semelhantes) para inferências futuras?
- Como deve ser apresentada a classificação de confiança para usuários que não são técnicos?
- Há requisitos específicos de auditoria ou conformidade que exigem manter registros de extração históricos?

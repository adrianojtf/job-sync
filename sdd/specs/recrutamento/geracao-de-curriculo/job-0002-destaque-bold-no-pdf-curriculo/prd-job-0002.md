# Documento de Requisitos de Produto (PRD)

## Visão Geral

Corrigir a geração de currículos em PDF para melhorar a legibilidade humana por meio de ênfase visual adequada. O problema atual é que o documento gerado apresenta todas as informações como texto simples, sem destaque para categorias técnicas, cargos ou nomes de formação, dificultando a leitura e a captura rápida de pontos relevantes.

Status de implementação atual:
- A correção já está implementada no gerador ReportLab atual, com destaque inline aplicado apenas aos elementos definidos por este PRD.
- A formatação é limitada à apresentação em PDF: não há alteração do conteúdo textual, da ordem das seções ou da estrutura do currículo.
- A validação foi realizada com testes automatizados em `tests/test_gerador_pdf.py`, que confirmam a geração de um PDF válido e a aplicação do markup de ênfase nas seções de Tecnologias, Experiências e Formação.

## Objetivos

- Destacar em negrito as categorias dentro da seção de Tecnologias para tornar mais fácil identificar rapidamente Languages, Frameworks, Web Development, DevOps, Databases, Version Control e Other.
- Destacar em negrito a linha de cabeçalho de cada experiência (nome da empresa e datas) e a posição ocupada para facilitar a leitura cronológica e a identificação de funções.
- Destacar em negrito títulos de formação e nomes de categoria na seção de Formação acadêmica para melhorar a compreensão da trajetória educacional.
- Preservar o layout atual do currículo em PDF e manter a compatibilidade com o mecanismo de geração ReportLab já existente.

## Histórias de Usuário

1. Como recrutador, eu quero ler um currículo em PDF onde as categorias de tecnologia e os cargos estão em negrito para captar rapidamente as informações mais importantes.
2. Como candidato, eu quero que meu currículo em PDF seja formatado de forma clara e profissional, com destaques visuais consistentes nas seções de tecnologia, experiência e formação.
3. Como desenvolvedor, eu quero uma correção que aproveite o gerador de PDF atual e foque apenas em reforçar a formatação sem alterar o conteúdo ou a estrutura de dados.

## Funcionalidades Principais

### 1. Ênfase em Tecnologias

- O sistema deve aplicar negrito às categorias dentro da seção de Tecnologias: Languages, Frameworks, Web Development, DevOps, Databases, Version Control e Other.
- Exemplo atual:
  - Languages: Python, Java, Go, TypeScript, JavaScript
  - Frameworks: Django, Hibernate, Spring Boot
  - Web Development: RESTful APIs, JSF, Microservices, Vue.js, SOAP, React, RabbitMQ, JSP
- O texto de conteúdo deve permanecer inalterado, mas as etiquetas de categoria devem aparecer com estilo de negrito no PDF.

Requisitos funcionais:
1. Aplicar formatação em negrito apenas às etiquetas de categoria dentro da seção de Tecnologias.
2. Manter os itens de tecnologia listados exatamente como estão, sem alterar a ordem ou o conteúdo.
3. Preservar que a seção de Tecnologias continue renderizando como parágrafos ou listas de bullets quando já houver marcadores.

### 2. Ênfase em Experiências

- O sistema deve aplicar negrito à linha que contém o nome da empresa e as datas de cada experiência.
- O sistema deve aplicar negrito à posição ocupada na experiência correspondente.
- O sistema deve inserir uma linha em branco entre cada experiência para melhorar a separação visual entre blocos de histórico profissional.
- Exemplo atual:
  - Starian Mar 2026 - Present
    Software Engineer
    Desenvolveu...
- Essa ênfase deve melhorar a leitura cronológica e o reconhecimento rápido do cargo e emprego.

Requisitos funcionais:
4. Detectar e renderizar com negrito o cabeçalho de empresa+período em cada bloco de experiência.
5. Detectar e renderizar com negrito o cargo/posição imediatamente abaixo desse cabeçalho.
6. Inserir espaçamento adicional (linha em branco) entre blocos de experiência para separar visualmente cada item.
7. Manter as descrições das atividades abaixo dos destaques como texto normal.

### 3. Ênfase em Formação Acadêmica

- O sistema deve aplicar negrito aos títulos de formação e aos nomes de categoria/instituição na seção de Formação acadêmica.
- Exemplo atual:
  - Education: Estácio, Jun 2022 - Jun 2024, Associate Degree in Systems Analysis and Development; IFSC, Dec 2013 - Dec 2015, Technical Degree in Telecommunications Technician
- A formatação deve separar claramente o curso/título e o tipo de formação, para facilitar a leitura humana.

Requisitos funcionais:
7. Detectar os blocos de formação e aplicar negrito aos elementos de título e categoria onde fizer sentido.
8. Manter a informação de datas e instituições como texto normal, exceto os títulos/categorias destacados.

### 4. Compatibilidade com o gerador de PDF existente

- A solução deve ser implementada no gerador de PDF atual do ReportLab, mantendo o mesmo fluxo de montagem do documento e os estilos já em uso.
- A alteração deve ser feita como ajuste de formatação de texto, não como uma mudança estrutural no modelo de dados de currículo.

Requisitos funcionais:
9. Usar markup inline compatível com ReportLab Paragraphs para aplicar negrito sem quebrar o parser de texto.
10. Validar que o PDF resultante continue renderizando corretamente quando o conteúdo contiver múltiplas linhas, bullets ou itens de tecnologia separados por vírgula.

## Experiência do Usuário

Personas:
- Recrutador: busca rapidamente os pontos-chave de um currículo sem perder tempo ao ler texto corrido.
- Desenvolvedor de produto: quer que a correção seja clara, pontual e mantenha a aparência profissional do currículo.
- Candidato: espera que seu perfil seja apresentado de forma legível e estruturada em um documento em PDF.

Jornada:
- O usuário solicita a geração do currículo em PDF.
- O sistema processa o currículo e aplica formatação de texto com ênfase em categorias relevantes.
- O usuário visualiza o PDF e percebe imediatamente os títulos de tecnologia, empresa, datas, posições e formação.

## Restrições Técnicas de Alto Nível

- A correção deve ser aplicada no gerador de PDF ReportLab atual.
- Não é permitido redesenhar completamente o layout do currículo ou adicionar novas seções.
- A prioridade é o destaque visual, não a transformação ou enriquecimento do conteúdo.
- Deve-se preservar compatibilidade com currículos gerados anteriormente e evitar mudanças que alterem o texto subjacente.

## Fora de Escopo

- Reformatação total do currículo em um novo layout visual.
- Alterar o conteúdo das seções para incluir ou remover tecnologias, experiências ou formações.
- Adicionar novos tipos de seções ou campos além de Tecnologias, Perfil, Experiências e Formação.
- Implementar um editor de currículos ou um novo mecanismo de geração de PDF fora do ReportLab.

## Questões em Aberto

- A seção de Formação acadêmica deve adotar um padrão de quebra de linha mais estruturado para melhorar ainda mais a leitura, ou apenas aplicar negrito aos elementos existentes?
- Devemos aplicar também negrito a outras legendas de seção secundárias, como "Perfil" ou títulos específicos dentro das descrições de experiência?
- Há múltiplos padrões de entrada de currículo que exigem uma lógica de detecção mais robusta para empresa/data/cargo, ou a abordagem atual com linhas identificáveis é suficiente?
- Queremos aproveitar esta correção para introduzir bullets reais no PDF onde hoje o texto é renderizado como parágrafos com marcadores manuais?

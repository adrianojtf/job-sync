# Documento de Requisitos de Produto (PRD) — JOB-0016

## Visão Geral

O PDF de currículo gerado pelo job-sync hoje tem um layout simples: nome alinhado à esquerda, títulos de seção em preto sem padrão de caixa, todas as linhas no mesmo tamanho e cor, e experiências descritas como blocos de texto corrido. Os tópicos separados por `-` (conquistas e resultados) se perdem: o texto ajustado pela IA vira prosa, e a seção de Tecnologias vira um único parágrafo.

Este PRD define a reformulação visual do PDF para ficar **igual ao modelo de referência** enviado pelo candidato (`modelo-referencia-curriculo-en.pdf`, nesta mesma pasta). O foco é a leitura humana: o recrutador deve achar em segundos empresa, período, cargo e resultados de cada experiência.

Analogia: hoje o PDF é uma folha de anotações. O modelo é uma planilha bem formatada. O conteúdo é o mesmo, mas a hierarquia visual (cor, peso, itálico, alinhamento e tópicos) diz ao leitor onde olhar primeiro.

### Relação com o JOB-0035

O JOB-0035 (já integrado à `main` pelo PR 47) mudou **o que** a IA entrega em cada experiência: conquistas em bullets e um parágrafo de contexto, como campos separados. Este JOB muda **como** o PDF desenha esse conteúdo. Os dois se encontram em um contrato de texto (ver seção 9):

| JOB | Responsabilidade |
|---|---|
| JOB-0016 (este) | Layout do PDF igual ao modelo; leitura do texto de experiência, formação e certificações; preservação de linhas e tópicos nas seções de Tecnologias e na extração |
| JOB-0035 | Campos de conquistas e contexto no domínio, na revisão e nas sugestões de IA; prompts de ajuste das experiências |

O JOB-0035 já está na `main` e deixou no gerador um desenho provisório do contexto (Helvetica Oblique, `#666666`). Este JOB substitui esse desenho pelo estilo do modelo (Carlito Itálico, `#595959`) e mantém os comportamentos que os testes do JOB-0035 garantem.

## Objetivos

- Reproduzir no PDF gerado o estilo e o design do modelo de referência (tipografia, cores, alinhamentos, linhas divisórias e espaçamentos).
- Garantir que cada tópico iniciado por `-` vire um item de lista com marcador `●` e recuo pendente (a segunda linha alinha com o texto, não com o marcador).
- Preservar a estrutura de linhas e tópicos do conteúdo original após o ajuste por IA.
- Manter o PDF compatível com leitura por ATS (texto selecionável, sem imagens no lugar de texto, ordem de leitura linear).

Métricas de sucesso:
- Comparação visual lado a lado com o modelo aprovada pelo candidato (critério de aceite manual).
- 100% dos tópicos `-` do conteúdo de entrada renderizados como itens de lista no PDF (verificado por teste automatizado).
- Texto extraído do PDF gerado (via `pdfplumber`) mantém a mesma ordem lógica do conteúdo do `Curriculo`.

## Histórias de Usuário

1. Como **recrutador**, eu quero ver empresa e período na mesma linha, com o período alinhado à direita, para entender a linha do tempo do candidato sem ler o texto.
2. Como **recrutador**, eu quero ler os resultados de cada experiência em tópicos com marcador, para escanear métricas (ex.: "95%", "5 milhões de tickets") rapidamente.
3. Como **candidato**, eu quero que o currículo adaptado para cada vaga tenha a mesma aparência profissional do meu modelo, para não precisar reformatar à mão.
4. Como **candidato**, eu quero que os tópicos que escrevi com `-` continuem como tópicos depois do ajuste da IA, para não perder a estrutura que montei.
5. Como **desenvolvedor**, eu quero que a mudança fique restrita ao adapter de PDF e às instruções de ajuste de texto, sem alterar o modelo de domínio `Curriculo`.

Casos extremos:
- Experiência sem tópicos (apenas contexto) — ex.: "Starian" no modelo.
- Experiência sem linha de contexto.
- Linha de cabeçalho sem período identificável.
- Currículo em português (`idioma_alvo = "pt"`) com rótulos traduzidos ("Contexto:", "Atual").
- Tópico longo que quebra em 2 ou 3 linhas.
- Seções opcionais (Certificações, Idiomas) presentes ou ausentes.

## Funcionalidades Principais

### 1. Página e tipografia

O que faz: define a base visual do documento conforme o modelo.

Requisitos funcionais:
1. A página deve usar o formato Carta (612 × 792 pt), com margens laterais de 45 pt, igual ao modelo.
2. A família tipográfica deve ser sans-serif humanista métrica-compatível com Calibri (o modelo usa **Carlito**), com variações Regular, Bold e Italic.
3. O documento deve usar a paleta do modelo:
   - Azul-marinho `#1F3864` para nome, títulos de seção, linhas divisórias e cargos.
   - Cinza `#595959` para contatos, períodos e texto de contexto.
   - Preto `#000000` para corpo de texto, rótulos de tecnologia, empresas e tópicos.
   - Azul de link `#0563C1`, sublinhado, para o perfil do LinkedIn.

### 2. Cabeçalho

Requisitos funcionais:
4. O nome completo deve aparecer **centralizado**, em **caixa alta**, negrito, 16 pt, azul-marinho.
5. A linha de contato deve aparecer centralizada, 10 pt, cinza, no formato `LinkedIn: <link> | Email: <email>`.
6. O endereço do LinkedIn deve ser um link clicável, azul e sublinhado.
7. Não deve haver linha divisória logo abaixo do cabeçalho (a primeira linha é a da primeira seção).

### 3. Títulos de seção

Requisitos funcionais:
8. Cada título de seção deve aparecer em **caixa alta**, negrito, 11 pt, azul-marinho, alinhado à esquerda.
9. Abaixo de cada título deve haver uma linha horizontal azul-marinho de 0,75 pt, ocupando toda a largura útil.
10. Os títulos devem respeitar o idioma alvo (ex.: `TECHNICAL SKILLS`, `PROFILE`, `EXPERIENCE`, `EDUCATION` em inglês; `TECNOLOGIAS`, `PERFIL`, `EXPERIÊNCIA`, `FORMAÇÃO ACADÊMICA` em português).
11. A ordem das seções deve seguir o modelo: Tecnologias → Perfil → Experiências → Formação → Certificações → Idiomas.

### 4. Seção de Tecnologias

Requisitos funcionais:
12. Cada categoria deve ocupar **uma linha própria**, no formato `**Rótulo:** itens`, com rótulo em negrito e itens em regular, 10,5 pt.
13. As linhas de categoria não devem ter marcador nem recuo.
14. O sistema não deve juntar categorias diferentes em um único parágrafo.

### 5. Seção de Perfil

Requisitos funcionais:
15. O resumo deve ser um parágrafo justificado à esquerda, 10,5 pt, preto, sem marcador.

### 6. Seção de Experiências

Cada experiência é um bloco com até quatro partes, nesta ordem visual:

| Parte | Estilo |
|---|---|
| Empresa (esquerda) + período (direita) na mesma linha | Empresa: negrito 11,5 pt preto. Período: regular 10,5 pt cinza |
| Cargo | Itálico 10,5 pt azul-marinho |
| Tópicos (`-`) | Marcador `●` recuado, texto regular 10,5 pt preto, recuo pendente |
| Contexto | Itálico 10,5 pt cinza, começando com `Context:` / `Contexto:` |

Requisitos funcionais:
16. O sistema deve separar o período (ex.: `Mar 2026 - Present`, `Nov 2022 - Mar 2026`) do nome da empresa e alinhá-lo à direita na mesma linha.
17. O cargo deve aparecer na linha abaixo da empresa, em itálico azul-marinho.
18. Cada linha iniciada por `-`, `•` ou `*` deve virar um item de lista com marcador `●`, recuo de 18 pt para o marcador e 36 pt para o texto.
19. Quando o texto de um tópico quebrar linha, a continuação deve alinhar com o início do texto, não com o marcador (recuo pendente).
20. Deve haver um pequeno espaço vertical entre tópicos consecutivos, como no modelo.
21. A linha de contexto deve ficar em itálico cinza, sem marcador, após os tópicos.
22. Deve haver espaço vertical visível entre uma experiência e a próxima.
23. Experiências sem tópicos ou sem contexto devem ser renderizadas sem deixar espaços vazios.
24. Quando o período não for identificado, a linha deve mostrar apenas a empresa, sem erro.

### 7. Seções de Formação, Certificações e Idiomas

Requisitos funcionais:
25. Cada formação deve seguir o padrão do modelo: instituição em negrito preto + período em cinza à direita; na linha abaixo, curso e grau em itálico azul-marinho.
26. Certificações devem seguir o mesmo padrão de Formação (nome/instituição + ano à direita).
27. Idiomas devem aparecer uma linha por idioma, com o idioma em negrito e o nível em regular.

### 8. Preservação de tópicos no ajuste por IA

O que faz: garante que o texto que chega ao gerador de PDF ainda tenha a estrutura de linhas e tópicos.

Requisitos funcionais:
28. O ajuste de texto por IA deve manter cada tópico `-` do original como um tópico `-` na saída (pode reescrever o texto do tópico, não pode juntá-los em prosa).
29. O ajuste da seção de Tecnologias deve manter uma categoria por linha, no formato `Rótulo: itens`.
30. O formato de bloco de experiência (cabeçalho, cargo, tópicos `-`, linha `Context:`/`Contexto:` e linha em branco entre experiências) é produzido pela IA nos ajustes de experiência, que pertencem ao JOB-0035. Este JOB só garante que o PDF desenhe esse formato (RF 16 a 24 e 32 a 34).
31. A extração do currículo a partir do PDF deve preservar as quebras de linha e os marcadores do texto original.

### 9. Contrato de texto compartilhado com o JOB-0035

O texto da seção de experiências chega ao PDF por dois caminhos: a IA que escreve o texto (fonte PDF) e a conversão dos campos estruturados do JOB-0035 e do Perfil Estruturado. O PDF deve aceitar os dois formatos de cabeçalho, sem mudar esses geradores.

Requisitos funcionais:
32. O PDF deve aceitar o cabeçalho no formato do modelo (`Empresa Período`, cargo na linha seguinte) e no formato `Cargo — Empresa (Período)`, com travessão e com os parênteses opcionais (o JOB-0035 os omite quando não há período). No segundo, a empresa vai em negrito com o período à direita e o cargo vai em itálico azul-marinho na linha abaixo.
33. Formação e certificações em `Curso — Instituição (Período)` e `Nome — Instituição (Ano)` seguem a mesma regra: instituição em negrito com o período à direita, e curso ou nome em itálico azul-marinho na linha abaixo.
34. A linha iniciada por `Context:` ou `Contexto:` deve ser desenhada em itálico cinza depois dos tópicos, com o rótulo incluído no texto exibido. O rótulo tem uma única fonte no sistema, `rotulos_experiencia.py` do JOB-0035, que este JOB reutiliza.

## Experiência do Usuário

- Persona primária: candidato que gera um currículo adaptado por vaga e envia o PDF direto ao portal.
- Persona secundária: recrutador que faz uma leitura de 6 a 10 segundos do PDF.
- Fluxo: o candidato gera o currículo adaptado (fluxo atual, sem novos passos) → baixa o PDF → o PDF já está no layout do modelo.
- Nenhuma tela nova. A mudança aparece apenas no arquivo gerado.
- Acessibilidade e ATS:
  - Texto real e selecionável (sem imagens).
  - Contraste dos tons de cinza e azul igual ao do modelo.
  - Ordem de leitura linear: empresa → período → cargo → tópicos → contexto.

## Restrições Técnicas de Alto Nível

- Manter o gerador de PDF atual baseado em ReportLab (sem dependência de LibreOffice, navegador ou serviço externo).
- A fonte usada deve ter licença que permita distribuição junto com o código (a Carlito usa SIL Open Font License).
- A fonte precisa estar disponível também na imagem Docker do backend (`python:3.12-slim`).
- Não alterar o contrato da porta `GeradorPdfPort` nem a estrutura do agregado `Curriculo`.
- Tempo de geração do PDF não deve aumentar de forma perceptível (meta: abaixo de 1 s por currículo de 2 páginas, sem contar chamadas de IA).
- Não enviar dados do currículo a nenhum serviço novo.
- Os testes do JOB-0035 sobre o contexto no PDF continuam valendo, trocando apenas fonte e cor para o estilo do modelo.

## Fora de Escopo

- Escolha de múltiplos modelos/temas de layout pela interface.
- Edição visual do currículo (cores, fontes, margens) pelo usuário.
- Foto, ícones ou layout em duas colunas.
- Mudanças no conteúdo gerado pela IA além da preservação de estrutura (RF 28 a 31).
- Geração em formato DOCX.
- Alteração da carta de apresentação ou de outros PDFs do sistema.
- Campos de conquistas e contexto no modelo de domínio, edição na revisão, sugestões de IA por experiência, prompts de ajuste das experiências e a regra de métricas estimadas: tudo isso é do JOB-0035.

## Questões em Aberto

1. **Período "Present"/"Atual":** o texto do período deve ser traduzido conforme o idioma alvo (`Present` → `Atual`) ou mantido como veio no conteúdo? Proposta: manter como veio; a IA já traduz o conteúdo.
2. **Posição do período:** no modelo, o período termina em ~513 pt, e não na margem direita (567 pt), o que parece efeito de tabulação do editor de origem. Devemos copiar essa posição exata ou alinhar na margem direita? Proposta: copiar a posição do modelo, para ficar igual.
3. **Marcador `●`:** no modelo o marcador usa outra fonte (Liberation Serif, 10 pt). Aceita-se usar o `●` da própria Carlito, se o resultado visual for equivalente?
4. **Rótulo "Context:" (resolvida com o JOB-0035):** o JOB-0035 sempre escreve o rótulo na última linha do bloco. O PDF desenha o rótulo como veio no texto. Linhas soltas sem rótulo, depois do cargo e dos tópicos, também vão para o contexto, sem rótulo.
5. **Currículo montado do Perfil Estruturado (resolvida):** `MontarCurriculoDoPerfilEstruturado` e o `para_texto` do JOB-0035 usam o formato `Cargo — Empresa (Período)`. O PDF passa a aceitar esse formato (RF 32 e 33), e nenhum dos dois geradores muda.
6. **Código JIRA:** foi usado `JOB-0016` (próximo número livre no repositório). Confirmar se este é o código correto.
7. **Cor do contexto (adotado, a confirmar):** o JOB-0035 implementou `#666666` com `Helvetica-Oblique`. Este JOB usa `#595959` com Carlito Itálico, medidos no modelo, porque o objetivo é ficar igual ao modelo. Os testes do JOB-0035 que fixam o estilo antigo são atualizados.
8. **Ordem de integração (resolvida):** o JOB-0035 entrou primeiro (PR 47). A `main` foi integrada a esta branch por merge, sem conflito.

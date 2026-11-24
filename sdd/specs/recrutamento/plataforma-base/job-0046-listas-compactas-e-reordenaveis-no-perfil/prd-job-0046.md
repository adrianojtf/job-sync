# Documento de Requisitos de Produto (PRD) — JOB-0046

## Visão Geral

Hoje, em Meu perfil, cada experiência ocupa uma tela inteira de campos abertos (identificação, contexto, responsabilidades, banco de conquistas e skills). Com cinco experiências, o usuário rola muito para achar uma delas. Formação, certificações, idiomas e tecnologias seguem o mesmo padrão de formulário sempre aberto. Além disso, a ordem dos itens só muda por remover e recriar: não há como reordenar.

Este PRD define dois ajustes para todas as listas do perfil:

- **Cartões compactos:** cada item aparece recolhido, com o resumo que permite reconhecê-lo, e abre para edição só quando o usuário quer.
- **Reordenação por arrastar e soltar:** o usuário muda a ordem dos itens, e essa ordem é a do currículo.

Listas cobertas: experiências, formação acadêmica, certificações, idiomas e tecnologias. Dados pessoais e resumo viram um cartão recolhível, sem reordenação.

O protótipo aprovado está em `sdd/prototipos/perfil_experiencias_prototipo.html` e é a referência visual e de interação.

Analogia: hoje o perfil é uma pasta com todas as folhas abertas sobre a mesa. Passa a ser uma pasta com abas: o usuário vê o índice, escolhe a aba que quer abrir e troca as abas de lugar.

Depende da JOB-0009 (perfil estruturado) e da JOB-0045 (quatro blocos por experiência).

## Objetivos

- Reduzir a rolagem em Meu perfil: um cartão recolhido ocupa cerca de 90 px de altura em tela larga, contra mais de 1.300 px de uma experiência aberta hoje.
- Permitir reordenar os itens de todas as listas por mouse, toque e teclado.
- Manter a ordem salva como a ordem usada no PDF e na adaptação.
- Não perder nenhuma função atual do perfil (quatro blocos, banco de conquistas, sugestões de IA, avaliação, estruturação de perfil antigo).

Como medir o sucesso:

- Com cinco experiências recolhidas, a lista cabe em uma tela de 900 px de altura.
- Qualquer item de qualquer lista muda de posição por mouse, toque e teclado, e a nova ordem persiste após salvar e recarregar.
- O PDF gerado e o currículo adaptado seguem a ordem salva.
- Nenhuma regressão nos testes do perfil (JOB-0009, JOB-0042, JOB-0043, JOB-0045).

## Histórias de Usuário

Persona principal: **candidato** que mantém o currículo mestre e o adapta para várias vagas.

1. Como candidato, eu quero ver cada experiência recolhida, com cargo, empresa, período e um resumo, para achar a que preciso sem rolar.
2. Como candidato, eu quero abrir só a experiência que vou editar, para focar nela.
3. Como candidato, eu quero arrastar uma experiência para outra posição, para pôr as mais relevantes primeiro no currículo.
4. Como candidato, eu quero reordenar formação, certificações, idiomas e tecnologias do mesmo jeito, para controlar a ordem de todo o currículo.
5. Como candidato que usa teclado ou leitor de tela, eu quero mover um item com as setas e ouvir a nova posição, para reordenar sem mouse.
6. Como candidato no celular, eu quero reordenar com toque e, se preferir, com botões de subir e descer.
7. Como candidato, eu quero ordenar por período com um clique e desfazer, para recuperar a ordem cronológica.
8. Como candidato, eu quero desfazer uma reordenação ou remoção, para corrigir um erro.

Casos extremos:

- Lista com um só item: a alça e os botões de mover ficam inativos.
- Lista vazia: mostra o convite a adicionar o primeiro item.
- Soltar o item fora da lista ou pressionar Esc: nada muda.
- Item novo: entra no topo e abre expandido, com o foco no primeiro campo.
- Perfil antigo (só descrição): o cartão mostra o selo "Formato antigo" e abre a descrição.
- Tecnologia repetida (ignorando maiúsculas e minúsculas): não é criada de novo.
- O usuário reordena e sai da tela sem salvar: o app pergunta antes de descartar.

## Funcionalidades Principais

### 1. Cartão recolhido (experiências, formação e certificações)

Requisitos funcionais:

1. Cada item deve aparecer recolhido ao abrir o perfil, com alça de arrasto, inicial da empresa ou instituição, título, subtítulo, período (ou ano) e botão de abrir.
2. O cartão de experiência deve mostrar, no subtítulo, a primeira linha do contexto (ou da descrição, no formato antigo) e, abaixo, chips com a contagem de responsabilidades, realizações e skills.
3. Bloco vazio deve aparecer como chip tracejado ("sem skills"); o perfil antigo deve mostrar o selo "Formato antigo".
4. O cartão de formação deve mostrar curso, instituição e período; o de certificação, nome, instituição e ano.
5. Clicar no cartão (fora da alça) ou no botão de abrir deve expandir os campos de edição do item; "Concluir" deve recolhê-lo.
6. Vários cartões podem ficar abertos ao mesmo tempo, e cada lista deve ter "Expandir todas" e "Recolher todas".
7. Os campos de edição abertos devem ser os que já existem hoje, incluindo os quatro blocos, o banco de conquistas e as sugestões de IA da experiência.

### 2. Idiomas e tecnologias

Requisitos funcionais:

8. Cada idioma deve ser uma linha editável (nome e nível), sem abrir, com alça, botões de mover e remover.
9. As tecnologias gerais devem ser tags que se criam (Enter ou vírgula), se excluem e se reordenam, no lugar do campo de texto separado por vírgula.
10. Tecnologia repetida, ignorando maiúsculas e minúsculas, não deve ser criada.
11. As skills das experiências que faltarem nas tecnologias (JOB-0045) devem entrar no fim da lista de tags ao salvar, e o aviso de tecnologias incluídas continua.

### 3. Reordenação

Requisitos funcionais:

12. O usuário deve poder arrastar um item pela alça (nas tags, pela própria tag) para outra posição da mesma lista, por mouse e por toque.
13. Durante o arrasto, os cartões abertos devem se recolher, para o usuário enxergar a lista inteira, e a tela deve rolar perto das bordas.
14. O usuário deve poder mover um item pelo teclado: Espaço pega, setas movem, Espaço solta, Esc cancela.
15. Cada item deve ter botões "Mover para cima" e "Mover para baixo", sempre visíveis no toque.
16. Cada movimento deve ser anunciado em português a leitores de tela, com o nome do item e a posição (ex.: "Software Engineer em Starian solto na posição 2 de 5").
17. Um item só se move dentro da própria lista.
18. Soltar fora da lista ou pressionar Esc deve manter a ordem original.
19. Experiências, formação, certificações e idiomas devem ter "Ordenar por período" (certificações, "por ano"), do mais recente para o mais antigo; tecnologias não têm ordenação automática.

### 4. Alterações pendentes

Requisitos funcionais:

20. Reordenar, adicionar ou remover um item deve contar como alteração não salva, sem gravar nada até o usuário clicar em "Salvar perfil".
21. Reordenação, remoção, adição e "Ordenar por período" devem ter "Desfazer" por alguns segundos.
22. "Descartar" deve restaurar a última versão salva, inclusive a ordem.
23. Ao sair do perfil com alterações não salvas, o app deve pedir confirmação.

### 5. Ordem no restante do produto

Requisitos funcionais:

24. A ordem salva de cada lista deve ser a usada para montar o currículo do perfil, o PDF e a adaptação à vaga.
25. A adaptação deve preservar a ordem das experiências do perfil na revisão do currículo adaptado.

## Experiência do Usuário

Jornada de reordenação:

1. O usuário abre Meu perfil e vê os cartões recolhidos.
2. Pega a alça de uma experiência; os cartões se recolhem e a lista fica à vista.
3. Solta na nova posição; o cartão pisca e aparece "Ordem alterada. Desfazer".
4. A barra "Alterações não salvas" oferece Descartar e Salvar perfil.

Requisitos de UI/UX:

- Mesmos componentes visuais e tokens do protótipo e do restante do app.
- Em telas estreitas, a inicial e o período saem do cartão e os chips descem para a linha de baixo.
- O cartão aberto mantém a identificação no topo e os blocos em duas colunas, como no protótipo.

Acessibilidade:

- A alça é focável, com `aria-roledescription` de item arrastável e nome com cargo, empresa e posição.
- Anúncios em português em cada passo (pegar, mover, soltar, cancelar), no padrão do board de candidaturas.
- Botões de mover e de abrir com rótulos acessíveis; o estado aberto é exposto (`aria-expanded`).
- Foco devolvido ao item após mover ou desfazer.
- Contraste adequado para chips e selos.

## Restrições Técnicas de Alto Nível

- Usar a biblioteca de arrastar e soltar que o projeto já adota, com suporte a mouse, toque e teclado.
- Sem campo novo na API: a ordem é a posição do item na lista salva, e o contrato atual do perfil continua válido.
- Nada é gravado enquanto o usuário reordena; só o salvar do perfil persiste.
- O endpoint que guarda a conquista aprovada usa a posição da experiência. Esse fluxo deve usar sempre o perfil salvo, e a tela não pode induzir a erro de posição por alteração não salva.
- A tela deve continuar acessível e responsiva (verificação com axe no E2E).
- Dados pessoais e textos do currículo não aparecem em logs.

## Fora de Escopo

- Arrastar um item para outra lista (ex.: mover uma tecnologia para uma experiência).
- Reordenar os itens internos de um cartão (responsabilidades, realizações e skills de uma experiência).
- Reordenar as seções do currículo (a ordem das seções do PDF continua a do layout).
- Ordenação automática contínua: a ordenação por período é uma ação pontual do usuário.
- Mudança de modelo de dados, migração ou campo de posição no banco.
- Reordenação na revisão do currículo adaptado (as competências por categoria já têm a sua, da JOB-0045).

## Questões em Aberto

1. **Aviso ao sair sem salvar:** não existe hoje nenhuma confirmação desse tipo no perfil. O requisito 23 a introduz; ela deve valer só para o perfil ou para todos os formulários?
2. **Ordenar períodos mistos:** períodos em texto livre ("Mar 2026 - Atual", "2020 - 2022") exigem ler o ano. Como tratar períodos sem ano legível (ex.: ordenar por último, sem mover)?
3. **Estado dos cartões ao recarregar:** voltar sempre recolhidos (proposta) ou lembrar o que estava aberto?
4. **Tags de tecnologias e ordem:** a sincronia com as skills (JOB-0045) acrescenta no fim da lista. Basta, ou o usuário prefere agrupá-las ao lado da skill de origem?
5. **Limite de itens:** há limite de experiências ou tecnologias para a performance do arrasto, ou nenhum limite é necessário?

# Documento de Requisitos de Produto (PRD) — JOB-0046

## Visão Geral

Hoje, em Meu perfil, cada experiência ocupa uma tela inteira de campos abertos. Com cinco experiências, o usuário rola muito para achar uma delas, e formação, certificações, idiomas e tecnologias seguem o mesmo padrão. A ordem dos itens só muda por remover e recriar.

Este PRD define dois ajustes para todas as listas do perfil:

- **Cartões compactos:** cada item aparece recolhido, com o resumo que permite reconhecê-lo, e abre para edição só quando o usuário quer.
- **Reordenação por arrastar e soltar:** o usuário muda a ordem dos itens, e essa ordem é a do currículo.

Listas cobertas: experiências, formação acadêmica, certificações, idiomas e tecnologias. Dados pessoais e resumo viram um cartão recolhível, sem reordenação.

O PRD também fecha três regras que protegem o usuário nessas listas: validação do formato do período, limite de 15 itens por lista e aviso ao sair com alterações não salvas.

O protótipo aprovado (`sdd/prototipos/perfil_experiencias_prototipo.html`) é a referência visual e de interação.

Depende da JOB-0009 (perfil estruturado) e da JOB-0045 (quatro blocos por experiência).

## Objetivos

- Reduzir a rolagem: um cartão recolhido ocupa cerca de 90 px em tela larga, contra mais de 1.300 px de uma experiência aberta hoje.
- Permitir reordenar os itens de todas as listas por mouse, toque e teclado.
- Manter a ordem salva como a ordem usada no PDF e na adaptação.
- Garantir que todo período salvo tenha formato válido, para a ordenação por período ser confiável.
- Não perder nenhuma função atual do perfil.

Como medir o sucesso:

- Com cinco experiências recolhidas, a lista cabe em uma tela de 900 px de altura.
- Qualquer item muda de posição por mouse, toque e teclado, e a ordem persiste após salvar e recarregar.
- Nenhuma regressão nos testes do perfil (JOB-0009, JOB-0042, JOB-0043, JOB-0045).

## Histórias de Usuário

Persona principal: **candidato** que mantém o currículo mestre e o adapta para várias vagas.

1. Como candidato, eu quero ver cada experiência recolhida, com cargo, empresa, período e um resumo, para achar a que preciso sem rolar.
2. Como candidato, eu quero abrir só a experiência que vou editar, para focar nela.
3. Como candidato, eu quero arrastar uma experiência para outra posição, para pôr as mais relevantes primeiro no currículo.
4. Como candidato, eu quero reordenar formação, certificações, idiomas e tecnologias do mesmo jeito, para controlar a ordem de todo o currículo.
5. Como candidato que usa teclado ou leitor de tela, eu quero mover um item com as setas e ouvir a nova posição.
6. Como candidato no celular, eu quero reordenar com toque ou com botões de subir e descer.
7. Como candidato, eu quero ordenar por período com um clique e desfazer, para recuperar a ordem cronológica.
8. Como candidato, eu quero desfazer uma reordenação ou remoção, para corrigir um erro.
9. Como candidato, eu quero que o perfil reabra com os cartões que eu deixei abertos, para continuar de onde parei.
10. Como candidato, eu quero ser avisado se o período que digitei está em formato inválido, para o currículo e a ordenação ficarem corretos.

Casos extremos:

- Lista com um só item: a alça e os botões de mover ficam inativos. Lista vazia: convite a adicionar o primeiro item.
- Soltar o item fora da lista ou pressionar Esc: nada muda.
- Item novo: entra no topo e abre expandido, com o foco no primeiro campo.
- Perfil antigo (só descrição): o cartão mostra o selo "Formato antigo".
- Tecnologia repetida (ignorando maiúsculas e minúsculas): não é criada de novo.
- O usuário reordena e sai da tela sem salvar: o app pergunta antes de descartar.
- Lista com 15 itens: o botão de adicionar fica desabilitado, com a explicação do limite.
- Perfil salvo antes desta regra, com período em formato livre ou mais de 15 itens: abre e mostra tudo; ao salvar, o app aponta o que precisa ser corrigido.

## Funcionalidades Principais

### 1. Cartão recolhido (experiências, formação e certificações)

Requisitos funcionais:

1. Cada item deve aparecer recolhido ao abrir o perfil, com alça de arrasto, inicial da empresa ou instituição, título, subtítulo, período (ou ano) e botão de abrir.
2. O cartão de experiência deve mostrar, no subtítulo, a primeira linha do contexto (ou da descrição, no formato antigo) e, abaixo, chips com a contagem de responsabilidades, realizações e skills.
3. Bloco vazio deve aparecer como chip tracejado ("sem skills"); o perfil antigo deve mostrar o selo "Formato antigo".
4. O cartão de formação deve mostrar curso, instituição e período; o de certificação, nome, instituição e ano.
5. Clicar no cartão (fora da alça) ou no botão de abrir deve expandir os campos de edição do item; "Concluir" deve recolhê-lo.
6. Vários cartões podem ficar abertos ao mesmo tempo, e cada lista deve ter "Expandir todas" e "Recolher todas".
7. O app deve lembrar quais cartões estavam abertos e reabri-los iguais ao recarregar a página ou voltar ao perfil. O que foi removido deixa de existir; item novo abre expandido. A preferência é do navegador do usuário e não é salva no perfil.
8. Os campos de edição abertos devem ser os que já existem hoje, incluindo os quatro blocos, o banco de conquistas e as sugestões de IA da experiência.

### 2. Idiomas e tecnologias

Requisitos funcionais:

9. Cada idioma deve ser uma linha editável (nome e nível), sem abrir, com alça, botões de mover e remover.
10. As tecnologias gerais devem ser tags que se criam (Enter ou vírgula), se excluem e se reordenam, no lugar do campo de texto separado por vírgula.
11. Tecnologia repetida, ignorando maiúsculas e minúsculas, não deve ser criada.
12. As skills das experiências que faltarem nas tecnologias (JOB-0045) devem entrar no fim da lista de tags ao salvar, e o aviso de tecnologias incluídas continua.

### 3. Reordenação

Requisitos funcionais:

13. O usuário deve poder arrastar um item pela alça (nas tags, pela própria tag) para outra posição da mesma lista, por mouse e por toque.
14. Durante o arrasto, os cartões abertos devem se recolher, para o usuário enxergar a lista inteira, e a tela deve rolar perto das bordas.
15. O usuário deve poder mover um item pelo teclado: Espaço pega, setas movem, Espaço solta, Esc cancela.
16. Cada item deve ter botões "Mover para cima" e "Mover para baixo", sempre visíveis no toque.
17. Cada movimento deve ser anunciado em português a leitores de tela, com o nome do item e a posição (ex.: "Software Engineer em Starian solto na posição 2 de 5").
18. Um item só se move dentro da própria lista.
19. Soltar fora da lista ou pressionar Esc deve manter a ordem original.
20. Experiências e formação devem ter "Ordenar por período", e certificações "Ordenar por ano", do mais recente para o mais antigo; idiomas e tecnologias não têm ordenação automática.

### 4. Período, ano e limite de itens

Requisitos funcionais:

21. O período de experiência e de formação deve seguir o formato `início - fim`, em que cada lado é `aaaa`, `mmm aaaa` (mês abreviado em português ou inglês) ou `mm/aaaa`, e o fim pode ser `Atual` ou `Presente`. O separador pode ser hífen ou travessão, com ou sem espaços. O início não pode ser depois do fim. O ano da certificação deve ter quatro dígitos.
22. Um período ou ano preenchido fora do formato deve ser recusado: o campo mostra o erro com um exemplo (ex.: "Use o formato Mar 2024 - Atual ou 2020 - 2022"), o perfil não é salvo e a API devolve erro de validação. Campo vazio continua permitido.
23. Cada lista deve aceitar no máximo 15 itens; ao chegar a 15, "Adicionar" fica desabilitado e explica o limite.
24. Importar um PDF ou estruturar um perfil antigo não deve gravar período inválido: o usuário vê o erro na revisão e corrige antes de salvar.

### 5. Alterações pendentes

Requisitos funcionais:

25. Reordenar, adicionar ou remover um item deve contar como alteração não salva, sem gravar nada até o usuário clicar em "Salvar perfil".
26. Reordenação, remoção, adição e "Ordenar por período" devem ter "Desfazer" por alguns segundos.
27. "Descartar" deve restaurar a última versão salva, inclusive a ordem.
28. Ao sair de qualquer formulário de edição com alterações não salvas (Meu perfil, revisão e edição do currículo adaptado e demais formulários do app), o app deve pedir confirmação, seja por navegar para outra tela, por fechar a aba ou por recarregar.

### 6. Ordem no restante do produto

Requisitos funcionais:

29. A ordem salva de cada lista deve ser a usada para montar o currículo do perfil, o PDF e a adaptação à vaga.
30. A adaptação deve preservar a ordem das experiências do perfil na revisão do currículo adaptado.

## Experiência do Usuário

Jornada de reordenação:

1. O usuário abre Meu perfil e vê os cartões recolhidos.
2. Pega a alça de uma experiência; os cartões se recolhem.
3. Solta na nova posição e aparece "Ordem alterada. Desfazer".
4. A barra "Alterações não salvas" oferece Descartar e Salvar perfil.

Requisitos de UI/UX:

- Mesmos componentes e tokens do protótipo e do restante do app.
- Em telas estreitas, a inicial e o período saem do cartão.

Acessibilidade:

- A alça é focável, com `aria-roledescription` de item arrastável e nome com cargo, empresa e posição.
- Anúncios em português em cada passo (pegar, mover, soltar, cancelar), no padrão do board de candidaturas.
- Botões de mover e de abrir com rótulos acessíveis; o estado aberto é exposto (`aria-expanded`).
- Foco devolvido ao item após mover ou desfazer; contraste adequado em chips e selos.

## Restrições Técnicas de Alto Nível

- Usar a biblioteca de arrastar e soltar que o projeto já adota, com suporte a mouse, toque e teclado.
- Sem campo novo na API: a ordem é a posição do item na lista salva, e o contrato atual do perfil continua válido.
- Nada é gravado enquanto o usuário reordena; só o salvar do perfil persiste.
- A validação do período vale na tela e na API (erro de validação), com o mesmo formato nos dois lados. É a única mudança de contrato desta JOB: dados já salvos continuam legíveis, mas só são regravados válidos.
- Os cartões abertos ficam guardados no navegador, por usuário, e não passam pela API.
- O endpoint que guarda a conquista aprovada usa a posição da experiência. Esse fluxo deve usar sempre o perfil salvo, e a tela não pode induzir a erro de posição por alteração não salva.
- A tela continua acessível e responsiva (axe no E2E).

## Fora de Escopo

- Arrastar um item para outra lista (ex.: mover uma tecnologia para uma experiência).
- Reordenar os itens internos de um cartão (responsabilidades, realizações e skills de uma experiência).
- Reordenar as seções do currículo (a ordem das seções do PDF continua a do layout).
- Mudança de modelo de dados, migração dos períodos já salvos ou campo de posição no banco (o usuário corrige ao salvar).
- Reordenação na revisão do currículo adaptado (as competências já têm a sua).

## Questões em Aberto

Decisões do produto já fechadas: o aviso ao sair vale para todos os formulários; período fora do formato é recusado; os cartões abertos são lembrados; a sincronia de skills acrescenta no fim; o limite é de 15 itens.

1. **Limite de 15 e tecnologias:** as skills das experiências entram nas tecnologias ao salvar (JOB-0045) e podem passar de 15 com facilidade. O limite vale também para tecnologias? Proposta: não, só para as demais listas.
2. **Perfis acima de 15 itens:** os já salvos abrem normalmente. Salvar exige cortar até 15?
3. **Período vazio:** continua permitido (requisito 22), mas ele fica fora da ordenação por período e permanece onde está. Algum campo deve ser obrigatório (ex.: período da experiência)?
4. **Normalização:** `2020-2022` e `2020 - 2022` são válidos. Gravar como digitado ou padronizar?
5. **Aviso ao sair:** além de Meu perfil e da revisão do currículo adaptado, quais formulários entram na primeira entrega?

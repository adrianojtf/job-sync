# Documento de Requisitos de Produto (PRD) — JOB-0041

## Visão Geral

Dois problemas aparecem hoje no currículo adaptado:

1. **Tecnologias em texto livre.** A seção de tecnologias é um campo de texto com muitos itens ("Linguagens: Java, Python, ..."). Para tirar ou incluir um item, o usuário edita o texto à mão. Com listas longas, isso é lento e propenso a erro.
2. **O currículo adaptado não é editável depois.** O rascunho revisado vira PDF e fica só na memória da tela. Ao voltar à tela do PDF ou fechar a tela, não há como corrigir o currículo, nem aproveitá-lo em outra vaga. Só o PDF final é guardado, ao confirmar a candidatura.

Este PRD define: (a) a seção de competências editada por categorias e tags, no modelo do currículo de referência (seção "Competências"); e (b) o currículo adaptado como objeto salvo, que pode ser reaberto para edição e usado como base em outras vagas.

Analogia: hoje o currículo é uma foto (o PDF). Com a mudança, ele passa a ser o arquivo de edição, e o PDF é só a foto tirada dele quando preciso.

Depende da JOB-0033 (revisão antes do PDF), da JOB-0037 (confirmação de candidatura na tela de ajuste) e da JOB-0016 (layout do PDF).

## Objetivos

- Editar competências por tags é mais rápido do que editar o texto.
- O usuário reabre e edita um currículo adaptado depois de gerado, inclusive após fechar a tela.
- Um currículo adaptado serve de base para outra vaga.

Como medir o sucesso:

- Remover ou incluir uma tecnologia leva uma ação (clique em remover, ou digitar e confirmar), sem editar texto corrido.
- Um currículo adaptado salvo é reaberto após recarregar a página e após novo login, com o mesmo conteúdo.
- O PDF baixado depois de uma edição reflete o conteúdo editado.
- Nenhuma regressão nos testes das JOB-0033, JOB-0034, JOB-0035 e JOB-0037.

## Histórias de Usuário

Persona principal: **candidato** que adapta o currículo para várias vagas.

1. Como candidato, eu quero ver as competências por categoria (Linguagens, Backend e APIs, Bancos de Dados etc.), como no meu currículo de referência, para entender e revisar cada grupo.
2. Como candidato, eu quero remover uma tecnologia clicando na sua tag, para não editar texto corrido.
3. Como candidato, eu quero criar uma tag nova em uma categoria, para incluir uma tecnologia que a IA não listou.
4. Como candidato, eu quero renomear, criar e excluir categorias, para adequar o currículo à vaga.
5. Como candidato, eu quero reabrir o currículo na tela do PDF e editá-lo, para corrigir algo sem refazer a adaptação.
6. Como candidato, eu quero reabrir o currículo depois de fechar a tela, para corrigir antes de enviar a candidatura.
7. Como candidato, eu quero usar um currículo adaptado como base de outra vaga, para não partir do zero.

Casos extremos:

- Excluir a última tag de uma categoria: a categoria fica vazia e é descartada ao salvar.
- Tag duplicada na mesma categoria (ignorando maiúsculas e minúsculas): não é criada de novo.
- Categoria com nome vazio: não é salva.
- Currículo editado já vinculado a uma candidatura: o PDF da candidatura passa a ser o editado.
- Currículo salvo removido pelo usuário: some da lista de bases; candidaturas existentes não quebram.
- Base com tecnologia trocada por equivalente em adaptação anterior (JOB-0037): ver Questões em Aberto.

## Funcionalidades Principais

### 1. Competências por categorias e tags

Requisitos funcionais:

1. A revisão do currículo adaptado deve mostrar as competências agrupadas em categorias, cada uma com um nome e uma lista de tags.
2. O usuário deve poder remover uma tag, e a tag removida deve sair do PDF.
3. O usuário deve poder criar uma tag em uma categoria digitando o texto e confirmando (Enter ou vírgula).
4. O usuário deve poder criar, renomear e excluir categorias.
5. O conteúdo gerado pela IA (texto "Categoria: item, item") deve aparecer já separado em categorias e tags.
6. Nomes de categoria renomeados ou criados pelo usuário devem sair no PDF como digitados, com o mesmo destaque das categorias conhecidas.
7. O comportamento deve ser o mesmo na revisão antes do PDF e na edição posterior.

### 2. Currículo adaptado como objeto salvo

8. Ao confirmar a revisão, o sistema deve salvar o currículo adaptado (conteúdo estruturado, cargo, empresa, idioma e dados da vaga usados) no perfil do usuário.
9. A tela do PDF gerado deve ter a ação "Editar currículo", que reabre a revisão com o conteúdo salvo.
10. Salvar uma edição deve regenerar o PDF e atualizar o conteúdo salvo. Se o currículo estiver vinculado a uma candidatura, o PDF da candidatura também deve ser atualizado.
11. O usuário deve poder reabrir um currículo adaptado depois de fechar a tela (ponto de entrada em Questões em Aberto).
12. As sugestões de IA na edição posterior devem usar a vaga original do currículo.

### 3. Reuso como base

13. "Ajustar para uma vaga" deve listar os currículos adaptados salvos como fonte, ao lado de Meu perfil e dos PDFs salvos.
14. Ao escolher um currículo adaptado como fonte, a adaptação parte do seu conteúdo e gera um novo currículo adaptado, sem alterar o original.

## Experiência do Usuário

Jornada: o usuário gera o currículo adaptado e vê a revisão. No bloco "Competências", cada categoria tem o nome editável, as tags com botão de remover e um campo para nova tag. Há ação para adicionar e excluir categoria. Confirma, vê o PDF e, se quiser mudar algo, usa "Editar currículo" e volta à mesma revisão.

Requisitos de UI/UX:

- Remover tag e excluir categoria não pedem confirmação, mas a revisão existente já avisa sobre alterações não confirmadas ao voltar.
- O resto da revisão (resumo, experiências, formação, idiomas) não muda.

Acessibilidade:

- Todas as ações de tag e categoria funcionam por teclado.
- Cada botão de remover tem nome acessível com o texto da tag (ex.: "Remover Java").
- Criação ou remoção de tag é anunciada para leitores de tela.

## Restrições Técnicas de Alto Nível

- Os dados ficam isolados por perfil (multi-tenant), como nas demais entidades.
- A edição posterior não chama a IA, salvo nas Sugestões de IA acionadas pelo usuário.
- O PDF é gerado pelo gerador existente.
- Carga: a lista de currículos adaptados por perfil deve abrir sem demora perceptível.

## Fora de Escopo

- Tags em "Meu perfil" (o campo de tecnologias do perfil mestre não muda nesta entrega).
- Reordenar categorias e tags (fica a ordem de criação).
- Autocompletar ou sugerir tags pela IA.
- Versionamento ou histórico de edições do currículo.
- Edição simultânea por mais de uma sessão.
- Novo layout do PDF.

## Questões em Aberto

1. **Layout do PDF.** O modelo de referência mostra o nome da categoria em coluna à esquerda e os itens separados por "•" à direita. O PDF atual mostra o nome em negrito na mesma linha. Esta entrega deve mudar o layout?
2. **Ponto de entrada após fechar a tela.** Opções: cartão do currículo na lista de Currículos, detalhe da candidatura, ou ambos. A proposta é ambos.
3. **Limite de currículos adaptados por perfil**, como existe para PDFs salvos.
4. **Base com troca de tecnologia (JOB-0037).** Se uma adaptação anterior trocou Angular por React, a nova adaptação trata o texto trocado como fato original. Aceitar, ou manter as trocas visíveis ao usar como base?
5. **Remover o currículo salvo ou a candidatura** remove também o currículo adaptado? A proposta é manter o currículo adaptado.

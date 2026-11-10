# Documento de Requisitos de Produto (PRD) — JOB-0038

## Visão Geral

O board de candidaturas mostra quatro colunas (Aplicado, Entrevista, Oferta, Rejeitado). Hoje, para mover uma candidatura, o candidato abre uma caixa de seleção dentro do cartão e escolhe o novo status. Para ver os dados, clica em um botão "Detalhes". Em telas pequenas, as colunas empilham em uma lista vertical longa. O visual é de lista de cartões simples, bem diferente dos boards que o candidato já conhece (Jira, Trello, Linear).

Este PRD define um board no estilo do Jira: o candidato arrasta o cartão para outra coluna, abre o detalhe clicando no título da vaga e usa o board com conforto no celular e no desktop.

Analogia: hoje o candidato move um post-it preenchendo um formulário ("mover para..."). Com o board novo, ele pega o post-it e o cola na outra coluna.

## Objetivos

- Mover uma candidatura em um gesto (arrastar e soltar), sem caixa de seleção.
- Abrir o detalhe com um clique no título, sem botão extra.
- Permitir ordenar os cartões dentro de cada coluna, e manter essa ordem ao recarregar.
- Usar o board em qualquer largura de tela, de celular a monitor grande.
- Aproximar o visual dos boards de mercado, para reduzir o tempo de aprendizado.

Como medir o sucesso:

- 100% das movimentações (entre colunas ou dentro da coluna) permanecem após recarregar a página.
- O board não gera rolagem horizontal da página inteira em nenhuma largura; só a área das colunas rola.
- Todas as ações do board funcionam por mouse, toque e teclado.
- Nenhuma violação de acessibilidade (axe) na tela de Candidaturas.

## Histórias de Usuário

Persona principal: **candidato** que acompanha várias candidaturas ao mesmo tempo e atualiza o board depois de cada resposta das empresas.

1. Como candidato, eu quero arrastar um cartão para outra coluna, para atualizar o status sem abrir formulário.
2. Como candidato, eu quero reordenar os cartões dentro de uma coluna, para destacar as vagas mais importantes no topo.
3. Como candidato, eu quero clicar no título da vaga para ver o detalhe, para não procurar um botão.
4. Como candidato, eu quero usar o board no celular, para atualizar uma candidatura logo depois de uma entrevista.
5. Como candidato que usa só o teclado, eu quero mover cartões sem mouse, para ter o mesmo acesso.
6. Como candidato, eu quero ver a coluna de destino destacada enquanto arrasto, para saber onde o cartão vai cair.

Casos extremos:

- Soltar o cartão fora de qualquer coluna (o cartão volta ao lugar de origem).
- Falha de rede ao salvar o movimento (o cartão volta e o candidato é avisado).
- Coluna vazia como destino.
- Muitos cartões em uma coluna (rolagem dentro da coluna durante o arrasto).
- Clique no título logo depois de arrastar (não deve abrir o detalhe).
- Dois movimentos seguidos em sequência rápida.

## Funcionalidades Principais

### F1. Arrastar e soltar entre colunas

O candidato move o cartão para outra coluna. A mudança aparece na hora e é salva em seguida.

Requisitos funcionais:

- **RF1.** O candidato pode arrastar um cartão de uma coluna e soltá-lo em outra, por mouse e por toque.
- **RF2.** Ao soltar, o status da candidatura passa a ser o da coluna de destino, e a data da mudança de status é registrada.
- **RF3.** A mudança aparece na tela imediatamente. Se o salvamento falhar, o cartão volta à posição anterior e um aviso de erro é exibido.
- **RF4.** Soltar fora das colunas ou pressionar Esc cancela o movimento, sem alterar nada.
- **RF5.** Todas as transições entre os quatro status continuam permitidas, como hoje.
- **RF6.** Uma coluna vazia aceita cartões soltos nela.

### F2. Ordenação dentro da coluna

- **RF7.** O candidato pode arrastar um cartão para cima ou para baixo dentro da mesma coluna.
- **RF8.** A posição do cartão em cada coluna é salva e preservada ao recarregar.
- **RF9.** Um cartão que muda de coluna entra na posição onde foi solto.
- **RF10.** Uma candidatura nova entra no topo da coluna Aplicado.
- **RF11.** Candidaturas que já existem antes desta entrega ficam ordenadas pela data de aplicação, da mais recente para a mais antiga, como hoje.

### F3. Abrir o detalhe pelo título

- **RF12.** O título da vaga no cartão é o único ponto de acesso ao detalhe. O botão "Detalhes" deixa de existir.
- **RF13.** O clique no título abre a janela de detalhe atual, com os mesmos dados (empresa, status, data, currículo usado, histórico).
- **RF14.** Arrastar o cartão nunca abre o detalhe. Só um clique ou toque simples abre.
- **RF15.** O título tem aparência de link (sublinhado ao passar o mouse) e pode ser acionado pelo teclado.

### F4. Remoção da caixa de seleção de status

- **RF16.** A caixa de seleção "Mover para" é removida de todos os cartões.
- **RF17.** O movimento por teclado substitui a seleção: o candidato foca o cartão, aperta Espaço para pegar, usa as setas para escolher a posição e aperta Espaço para soltar (Esc cancela).
- **RF18.** Cada passo do movimento por teclado é anunciado a leitores de tela, em português.
- **RF18a.** O detalhe da candidatura (janela aberta pelo título) tem o campo **"Mover para"** com os quatro status. Ele é a alternativa sem arrastar, para quem não consegue ou não quer arrastar.
- **RF18b.** Escolher um status em "Mover para" move a candidatura para o topo da coluna escolhida, mostra o aviso "Candidatura movida para X" e atualiza o status exibido no próprio detalhe e no board atrás. Em caso de erro, o campo volta ao status anterior e o aviso de erro aparece.

### F5. Layout responsivo no estilo Jira

- **RF19.** As colunas têm largura fixa e ficam lado a lado. Quando não cabem na tela, a área do board rola na horizontal, sem empilhar as colunas.
- **RF20.** No celular, cada coluna ocupa quase toda a largura da tela e a rolagem horizontal encaixa em uma coluna por vez.
- **RF21.** A altura do board aproveita a tela. Cada coluna rola na vertical por conta própria, e o cabeçalho da coluna permanece visível.
- **RF22.** Durante o arrasto perto da borda da área do board ou da coluna, a rolagem acontece sozinha.
- **RF23.** O board se adapta ao tamanho da janela sem perder as posições dos cartões.

### F6. Visual condizente com boards de mercado

- **RF24.** O cabeçalho da coluna mostra o nome do status em destaque discreto, a contagem de cartões e uma marca de cor do status.
- **RF25.** O cartão mostra: título da vaga, empresa (com inicial em um marcador visual) e tempo desde a aplicação (por exemplo, "há 3 dias"). Os dados vêm só do que o sistema já guarda.
- **RF26.** Durante o arrasto, o cartão levantado tem sombra e leve inclinação. O lugar de origem mostra um espaço reservado, e a coluna de destino fica destacada.
- **RF27.** O estado vazio da coluna indica que dá para soltar cartões ali.
- **RF28.** O cartão reage ao mouse (cursor de arrasto, realce) e ao foco do teclado, com contraste suficiente.
- **RF29.** O visual segue os tokens do design system existente (cores, raios, tipografia), sem criar uma paleta paralela.

## Experiência do Usuário

- **Fluxo principal:** abrir Candidaturas, pegar o cartão, soltar na coluna, ver o aviso "Candidatura movida para Entrevista".
- **Toque:** o arrasto começa após um toque curto e firme sobre o cartão, para não conflitar com a rolagem da tela. O clique simples no título abre o detalhe.
- **Sem arrastar:** o candidato clica no título e usa "Mover para" no detalhe.
- **Teclado:** Tab chega ao cartão e ao título. Espaço no cartão inicia o movimento; Enter no título abre o detalhe.
- **Leitor de tela:** anúncios em português ("Candidatura X pega. Posição 2 de 4 em Entrevista.").
- **Acessibilidade:** mantém o padrão atual do projeto (WCAG AA, teste com axe). Movimento reduzido: com `prefers-reduced-motion`, as animações são cortadas.
- **Estados:** carregando, erro com "Tentar novamente" e vazio permanecem como hoje.

## Restrições Técnicas de Alto Nível

- O board continua usando as candidaturas do perfil ativo e o mesmo agrupamento por status.
- A ordem dos cartões passa a ser dado persistido por coluna; o armazenamento atual (SQLite) precisa ser estendido sem perder candidaturas existentes.
- A resposta de listagem continua agrupada por status, para não quebrar quem já a consome.
- O movimento precisa ser salvo de forma consistente: ou toda a mudança de coluna e posição vale, ou nenhuma.
- Navegadores alvo: os mesmos do restante do app, incluindo Safari iOS e Chrome Android.
- Sem novos serviços externos.

## Fora de Escopo

- Criar, editar ou excluir candidaturas pelo board.
- Novas colunas, colunas personalizadas ou limite de cartões por coluna (WIP).
- Filtros, busca, agrupamento por raias, rótulos, responsáveis, prioridade ou datas-limite no cartão.
- Seleção e movimento de vários cartões de uma vez.
- Colaboração em tempo real entre usuários.
- Histórico completo de mudanças de status (continua só a mudança mais recente).
- Rota própria para o detalhe da candidatura. O detalhe continua em janela sobre o board.
- Mudanças na tela de detalhe além do acesso por título e do campo "Mover para".
- Escolher a posição exata dentro da coluna pelo campo "Mover para" (a posição fina é feita arrastando).

## Questões em Aberto

1. **Alternativa ao arrasto por ponteiro único.** Resolvida: o campo "Mover para" fica dentro do detalhe (RF18a e RF18b), o que atende a alternativa de ponteiro único pedida pela WCAG 2.2 (critério 2.5.7, nível AA).
2. **Rolagem do cartão no toque.** O tempo de espera para iniciar o arrasto por toque (sugestão: 200 ms) precisa de validação em aparelhos reais.
3. **Marca de cor por status.** As cores de cada coluna (por exemplo, azul para Aplicado, âmbar para Entrevista, verde para Oferta, cinza para Rejeitado) precisam de aprovação de design.
4. **"Check box de seleção de status".** Este PRD interpreta o pedido como a remoção da caixa de seleção (`select`) "Mover para" dos cartões. Confirmar se havia outro controle em mente.

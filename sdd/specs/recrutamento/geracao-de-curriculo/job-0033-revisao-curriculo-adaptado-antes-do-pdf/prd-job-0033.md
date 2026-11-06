# Documento de Requisitos de Produto (PRD) — JOB-0033

## Visão Geral

Hoje, na tela "Ajustar para uma vaga", o clique em "Gerar currículo adaptado" executa a adaptação via IA e já devolve o PDF pronto. O usuário não vê o texto que a IA escreveu antes de o PDF existir. Se a IA errar um cargo, inventar um termo ou traduzir mal uma seção, o usuário só descobre no PDF e não tem como corrigir sem editar o arquivo fora do sistema.

Este PRD insere uma etapa de revisão entre a adaptação e o PDF. A IA produz um **rascunho do currículo adaptado**. O sistema mostra esse rascunho organizado por seção, no mesmo formato da tela de cadastro ("Meu perfil"). O usuário edita livremente qualquer parte e, quando estiver satisfeito, confirma com uma única ação. Só então o PDF é gerado, a partir do conteúdo revisado.

Analogia: hoje a IA "imprime direto". Com esta mudança, ela entrega uma "prova de impressão" que o usuário corrige antes de mandar para a gráfica.

## Objetivos

- Dar ao usuário controle sobre o conteúdo final do currículo antes do PDF.
- Garantir que o PDF reflita exatamente o conteúdo revisado, e não o texto bruto da IA.
- Reaproveitar a interface de cadastro de currículo, sem duplicar formulários (DRY).
- Manter o comportamento atual dos fluxos legados (app Streamlit e download direto da API).

Como medir o sucesso:

- 100% dos PDFs gerados pela tela "Ajustar para uma vaga" passam pela confirmação do usuário.
- Nenhuma divergência entre o conteúdo exibido na revisão no momento da confirmação e o conteúdo do PDF.
- Nenhuma regressão na tela "Meu perfil" após o reaproveitamento dos componentes.

## Histórias de Usuário

Persona principal: **candidato** que adapta o currículo mestre (ou um PDF da biblioteca) para uma vaga específica.

1. Como candidato, eu quero ver todo o currículo adaptado pela IA antes do PDF, para conferir se o conteúdo está correto.
2. Como candidato, eu quero editar qualquer seção (dados pessoais, resumo, experiências, formação, tecnologias etc.) em qualquer ordem, para corrigir erros da IA sem salvar seção por seção.
3. Como candidato, eu quero adicionar ou remover uma experiência no rascunho, para ajustar o foco do currículo à vaga.
4. Como candidato, eu quero confirmar uma única vez e receber o PDF, para que o arquivo final contenha exatamente o que revisei.
5. Como candidato, eu quero voltar aos dados da vaga sem gerar o PDF, para refazer a adaptação se o resultado não servir.
6. Como candidato que usa um PDF da biblioteca como fonte, eu quero revisar o conteúdo da mesma forma, mesmo que as experiências apareçam como um bloco de texto.

Casos extremos:

- O usuário apaga todo o conteúdo de uma seção: a seção não aparece no PDF.
- O usuário apaga o nome completo: o sistema bloqueia a confirmação e indica o campo.
- O usuário sai da revisão com alterações não confirmadas: o sistema pede confirmação antes de descartar.
- O usuário recarrega a página durante a revisão: o rascunho se perde e ele volta ao formulário da vaga (comportamento aceito nesta versão).

## Funcionalidades Principais

### 1. Rascunho do currículo adaptado

A adaptação via IA passa a produzir um rascunho em vez de um PDF. O rascunho contém todo o conteúdo adaptado: dados pessoais, seções de texto e, quando a fonte é o perfil estruturado, a lista de experiências com cargo, empresa, período e descrição.

Por que importa: separa "o que a IA escreveu" de "o que vira PDF". Assim, o usuário pode intervir entre os dois.

Requisitos funcionais:

1. Ao clicar em "Gerar currículo adaptado", o sistema deve executar a adaptação via IA e exibir a tela de revisão, sem gerar o PDF.
2. O rascunho deve conter todo o conteúdo adaptado pela IA, sem omitir seções.
3. Quando a fonte for o perfil estruturado, as experiências devem vir como itens individuais (cargo, empresa, período, descrição).
4. Quando a fonte for um PDF da biblioteca, as experiências devem vir como um bloco de texto.
5. As avaliações automáticas já existentes (avaliação da vaga e avaliação de cada experiência) devem continuar disponíveis junto com o rascunho.

### 2. Tela de revisão

A tela mostra o rascunho organizado por seção, em blocos identificados, com o mesmo visual da tela "Meu perfil". A divisão por seção é só visual: todos os campos ficam editáveis ao mesmo tempo.

Requisitos funcionais:

6. A tela deve exibir, em blocos separados: dados pessoais (nome, e-mail, LinkedIn, resumo profissional), experiências profissionais, tecnologias, formação acadêmica, certificações e idiomas — apenas as seções presentes no rascunho.
7. Os dados pessoais e as experiências estruturadas devem usar os mesmos campos, rótulos e validações da tela "Meu perfil".
8. Formação, certificações, idiomas e tecnologias devem aparecer como texto editável dentro do bloco da seção correspondente.
9. Todos os campos de todas as seções devem estar editáveis simultaneamente, sem botão de salvar por seção.
10. O usuário deve poder adicionar e remover experiências estruturadas no rascunho.
11. O usuário deve poder avaliar uma experiência do rascunho com a ação "Avaliar" já existente.
12. A tela deve oferecer a ação "Voltar para a vaga", que descarta o rascunho após confirmação, quando houver alterações.
13. A tela não deve alterar o currículo mestre ("Meu perfil") nem os PDFs da biblioteca.

### 3. Confirmação e geração do PDF

Uma única ação confirma o rascunho inteiro e gera o PDF.

Requisitos funcionais:

14. A tela deve ter uma única ação de confirmação ("Confirmar e gerar PDF").
15. A confirmação deve validar o rascunho inteiro. Se houver erro (ex.: nome vazio, experiência sem cargo ou empresa), o PDF não deve ser gerado e os campos com erro devem ser indicados.
16. O PDF deve ser gerado a partir do estado atual de todas as seções no momento da confirmação.
17. Seções deixadas vazias pelo usuário não devem aparecer no PDF.
18. O nome do arquivo deve seguir o padrão atual (nome, cargo, empresa, data), usando o nome completo revisado.
19. Após a geração, o sistema deve disponibilizar o download do PDF, como hoje.
20. A carta de apresentação e a análise ATS continuam funcionando como hoje, de forma independente da revisão.

### 4. Compatibilidade com fluxos legados

Requisitos funcionais:

21. O app Streamlit deve continuar gerando o PDF diretamente após a adaptação.
22. A API de adaptação existente, inclusive o download direto do PDF, deve manter o contrato e o comportamento atuais.

## Experiência do Usuário

Jornada principal:

1. O usuário preenche os dados da vaga e escolhe a fonte do currículo (perfil ou PDF).
2. Clica em "Gerar currículo adaptado". O botão mostra o aviso de espera atual ("pode levar até 1 minuto").
3. A tela de revisão substitui os painéis de resultado. Ela mostra um aviso curto: "Revise o conteúdo sugerido pela IA. O PDF só será gerado quando você confirmar."
4. O usuário edita qualquer campo, em qualquer ordem.
5. Clica em "Confirmar e gerar PDF". O botão mostra estado de carregamento.
6. O sistema volta à visão de resultados, com o arquivo pronto para "Baixar PDF".

Requisitos de UI/UX:

- Mesmo layout, painéis, campos e mensagens de erro da tela "Meu perfil".
- Indicação de "Alterações não confirmadas" no rodapé, como em "Meu perfil".
- Ação primária única no rodapé ("Confirmar e gerar PDF") e ação secundária "Voltar para a vaga".
- Em caso de falha na geração do PDF, o rascunho e as edições devem ser preservados e uma mensagem de erro deve aparecer.

Acessibilidade:

- Manter os padrões já usados nos componentes compartilhados: rótulos associados, erros ligados por `aria-describedby`, foco no primeiro campo com erro.
- A troca entre formulário da vaga e revisão deve ser anunciada a leitores de tela (título de seção com foco ou região `aria-live`).
- A tela deve continuar passando nos testes automáticos de acessibilidade existentes.

## Restrições Técnicas de Alto Nível

- Arquitetura hexagonal: a geração do PDF deve ficar desacoplada da adaptação via IA. A adaptação não deve mais depender da porta de geração de PDF.
- O rascunho deve ser tratado como um único objeto, com as seções como partes dele. A confirmação é atômica.
- O rascunho não é persistido no servidor nesta versão. Ele vive na sessão da tela até a confirmação.
- A interface deve reaproveitar os componentes da tela "Meu perfil", sem cópia de formulários.
- A regra do projeto restringe mudanças de contrato de API. O contrato atual de adaptação deve ser mantido; os novos comportamentos entram por novos recursos.
- Sem nova chamada à IA na confirmação: o PDF usa apenas o conteúdo revisado.
- Dados pessoais do rascunho não devem aparecer em logs.

## Fora de Escopo

- Persistir o rascunho no servidor ou permitir retomar a revisão após recarregar a página.
- Salvar o conteúdo revisado no currículo mestre ou na biblioteca de currículos.
- Editar estruturadamente formação, certificações e idiomas no rascunho (ficam como texto nesta versão).
- Adicionar seções que a IA não devolveu.
- Editar os títulos das seções.
- Pré-visualizar o PDF dentro da tela de revisão.
- Recalcular automaticamente o ATS Score ou a carta com base no conteúdo revisado.
- Alterar o fluxo do app Streamlit ou o fluxo de candidatura em vaga externa.

## Questões em Aberto

1. Vale a pena, em uma versão futura, devolver formação, certificações e idiomas estruturados pela IA, para usar os mesmos campos do cadastro também nessas seções?
2. A perda do rascunho ao recarregar a página será aceitável na prática? Se não for, uma versão futura pode guardar o rascunho na sessão do navegador.
3. O usuário deve poder salvar o conteúdo revisado como um novo PDF na biblioteca diretamente da tela de revisão?
4. O ATS Score deve passar a usar o conteúdo revisado em vez do currículo original?

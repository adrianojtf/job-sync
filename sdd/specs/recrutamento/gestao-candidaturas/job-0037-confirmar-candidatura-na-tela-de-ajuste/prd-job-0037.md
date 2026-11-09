# Documento de Requisitos de Produto (PRD) — JOB-0037

## Visão Geral

Na tela "Ajustar para uma vaga", o candidato adapta o currículo, revisa e gera o PDF. Depois disso, o fluxo acaba: para registrar que vai se candidatar, ele precisa sair da tela, cadastrar a vaga, salvar o PDF na biblioteca de currículos e só então criar a candidatura no board. São três passos manuais, e o PDF que ele acabou de gerar não fica ligado à candidatura.

Este PRD define o botão **"Confirmar candidatura"**. Com um clique, o sistema registra a candidatura no board, na coluna **Aplicado**, já com os dados da vaga e com o PDF gerado.

Analogia: hoje o candidato imprime o currículo e depois vai ao arquivo anotar, à mão, que o enviou. O botão faz a anotação e arquiva a cópia no mesmo gesto.

## Objetivos

- Registrar a candidatura em um clique, a partir da tela de ajuste.
- Manter o PDF exato que o candidato gerou ligado à candidatura, para consultá-lo depois.
- Eliminar os passos manuais de cadastrar vaga e salvar currículo.

Como medir o sucesso:

- 100% das candidaturas confirmadas aparecem no board, em Aplicado, com empresa, cargo e PDF.
- Nenhuma confirmação deixa registro pela metade (vaga, currículo ou candidatura sem os outros).
- Nenhum passo fora da tela de ajuste é necessário para registrar a candidatura.

## Histórias de Usuário

Persona principal: **candidato** que adapta o currículo para uma vaga e vai se candidatar pelo site da empresa.

1. Como candidato, eu quero confirmar a candidatura logo depois de gerar o PDF, para não esquecer de registrá-la.
2. Como candidato, eu quero que a candidatura nasça com empresa e cargo, para não digitar de novo.
3. Como candidato, eu quero abrir o PDF que usei em cada candidatura, para lembrar exatamente o que enviei.
4. Como candidato, eu quero ser avisado quando a biblioteca estiver cheia, para saber o que fazer.
5. Como candidato, eu quero ir ao board direto da confirmação, para ver a candidatura criada.

Casos extremos:

- Biblioteca com 10 currículos (limite por perfil).
- Falha no meio da confirmação (rede ou banco).
- Clique duplo no botão ou confirmação repetida da mesma geração.
- Candidato que edita a revisão e gera outro PDF depois de confirmar.

## Funcionalidades Principais

### 1. Botão "Confirmar candidatura"

Requisitos funcionais:

1. A tela deve mostrar o botão "Confirmar candidatura" junto do "Baixar PDF", somente quando houver um PDF gerado.
2. A empresa e o cargo da candidatura devem ser os informados na tela de ajuste. A tela já exige a empresa para gerar o currículo, então o botão não precisa de um estado para empresa em branco.
3. Durante o envio, o botão deve ficar desabilitado e indicar que está em andamento.

### 2. Registro da candidatura

Requisitos funcionais:

4. Ao confirmar, o sistema deve criar uma candidatura no status **Aplicado**, com a empresa e o cargo informados na tela de ajuste.
5. O sistema deve guardar a descrição da vaga digitada como uma vaga do perfil, já marcada como convertida em candidatura. Ela não deve aparecer em "Vagas salvas".
6. O sistema deve guardar o PDF gerado na biblioteca de currículos do perfil, com o nome do arquivo gerado, e ligá-lo à candidatura.
7. As três partes (vaga, currículo e candidatura) devem ser criadas juntas. Se alguma falhar, nada do que foi criado deve permanecer visível ao usuário.
8. O PDF ligado à candidatura deve ser exatamente o que o candidato gerou na tela.

### 3. Feedback e erros

Requisitos funcionais:

9. Em caso de sucesso, a tela deve mostrar "Candidatura confirmada em Aplicado" com o link "Ver no board", e o botão deve mudar para o estado confirmado, desabilitado.
10. Se a biblioteca tiver 10 currículos, o sistema não deve criar nada e deve avisar: "Sua biblioteca de currículos está cheia. Remova um currículo para confirmar a candidatura."
11. Em qualquer outra falha, a tela deve mostrar a mensagem de erro e permitir tentar de novo.
12. Se o candidato gerar um novo PDF depois de confirmar, o botão deve voltar ao estado inicial para uma nova confirmação.

### 4. Consulta posterior

Requisitos funcionais:

13. A candidatura deve aparecer no board, na coluna Aplicado, com empresa e cargo.
14. O detalhe da candidatura deve oferecer o botão "Baixar PDF" do currículo ligado a ela. Se o currículo foi removido da biblioteca, o detalhe avisa "Removido da biblioteca" e não oferece o download.

## Experiência do Usuário

Jornada:

1. O candidato gera o currículo adaptado e baixa o PDF (fluxo atual).
2. No mesmo cartão do PDF, clica em "Confirmar candidatura".
3. Vê "Candidatura confirmada em Aplicado" e clica em "Ver no board" quando quiser.

Requisitos de UI/UX:

- Mesmos componentes de botão, mensagem de erro e estado de carregamento das outras telas.
- O botão primário continua sendo "Baixar PDF". "Confirmar candidatura" é uma ação secundária ao lado dele.
- A mensagem de sucesso e a de erro são anunciadas para leitores de tela, e o foco não se perde.

## Restrições Técnicas de Alto Nível

- A candidatura nasce com o status `APLICADO`. Nenhum status novo é criado.
- A candidatura continua apontando para uma vaga e para um currículo salvo, por identificador.
- O limite de 10 currículos por perfil continua valendo, e a regra passa a ter um único lugar no sistema.
- O PDF e a descrição da vaga são dados pessoais: não aparecem em logs.
- Sem mudança nos endpoints existentes. A confirmação usa um endpoint novo.

## Fora de Escopo

- Novo status ou nova coluna no board (por exemplo, "Em andamento").
- Enviar o currículo à empresa ou integrar com portais de vagas.
- Substituir um currículo da biblioteca quando ela estiver cheia.
- Evitar candidaturas duplicadas no servidor (o botão só protege a mesma geração de PDF).
- Anexar a carta de apresentação à candidatura.
- O app Streamlit.

## Questões em Aberto

1. **Biblioteca poluída:** a biblioteca é também a lista de currículos-base para adaptar. Cada confirmação adiciona um PDF já adaptado a ela, que pode aparecer como opção de base. Vale marcar esses PDFs como "enviados em candidaturas" e escondê-los da lista de bases, em outro JOB?
2. **Limite de 10:** o candidato que confirma muitas candidaturas atinge o limite rápido. Aumentar o limite ou separar os PDFs de candidaturas da biblioteca?
3. **Duplicidade:** confirmar a mesma empresa e cargo duas vezes cria duas candidaturas. Avisar o candidato antes?
4. **Empresa em branco (resolvida):** a tela de ajuste já exige a empresa para gerar o currículo, então não há como chegar ao PDF sem ela.
5. **Código do JOB:** foi usado `JOB-0037`, o próximo número livre. Confirmar.

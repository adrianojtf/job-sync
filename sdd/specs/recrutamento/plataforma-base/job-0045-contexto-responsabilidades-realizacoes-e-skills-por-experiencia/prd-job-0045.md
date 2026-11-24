# Documento de Requisitos de Produto (PRD) — JOB-0045

## Visão Geral

Hoje cada experiência do perfil guarda uma descrição em texto livre. Só o currículo adaptado separa "conquistas" e "contexto" (JOB-0035). O perfil, a leitura do currículo inicial e o currículo gerado não têm essa estrutura, e as skills de cada experiência não existem como dado.

Este PRD faz cada experiência ter **quatro blocos separados**, em todo o produto:

- **Contexto (Context):** parágrafo curto sobre a empresa, a área, o time e o impacto do papel.
- **Principais responsabilidades (Key Responsibilities):** lista do que o candidato faz no dia a dia.
- **Principais realizações (Key Achievements):** lista de entregas, com resultado medido quando possível.
- **Skills (Technologies):** tags de tecnologias e competências usadas na experiência.

Os blocos valem em quatro lugares:

1. leitura do currículo inicial (PDF);
2. perfil estruturado e sua edição;
3. currículo gerado a partir do perfil;
4. currículo adaptado a uma vaga, incluindo a tela de revisão.

Na leitura do currículo inicial, o sistema tenta reconhecer os blocos no texto. O que não for reconhecido a IA gera.

Este PRD estende a JOB-0035 (conquistas e contexto só no adaptado) e muda uma de suas decisões: o perfil passa a guardar os blocos.

Exemplo de referência (idioma inglês):

```
Context: At Starian, one of Brazil's leading ERP companies for the construction industry, I am responsible for ...
Key Responsibilities:
- End-to-end ownership of features within an enterprise ERP platform ...
Key Achievements:
- Contributed to the evolution of ERP financial capabilities supporting more than 1,000 users.
Technologies: Java | PostgreSQL | SQL | REST APIs | React | JavaScript | JSP | WildFly | Flyway | ERP | SDD
```

Depende da JOB-0009 (perfil estruturado), JOB-0035 (conquistas e contexto), JOB-0041 (competências em tags), JOB-0042 (banco de conquistas) e JOB-0043 (perguntas de elucidação).

## Objetivos

- Toda experiência do perfil, do currículo gerado e do adaptado tem os quatro blocos.
- A leitura do currículo inicial reconhece os blocos existentes e a IA completa os ausentes, sem reescrever os reconhecidos.
- As skills por experiência são editadas como tags, como as tecnologias do perfil.
- As tecnologias gerais do perfil incluem automaticamente toda skill de experiência que ainda não consta nelas.
- Perfis antigos, com descrição livre, migram para o padrão com confirmação do usuário.

Como medir o sucesso:

- 100% das experiências lidas de um currículo inicial saem com os quatro blocos preenchidos (reconhecidos ou gerados).
- 100% das skills de experiência aparecem nas tecnologias gerais após salvar o perfil.
- Os rótulos do PDF e das telas seguem o idioma do currículo em 100% dos casos testados (português e inglês).
- Nenhuma regressão nos testes das JOB-0033, JOB-0034, JOB-0035, JOB-0041 e JOB-0042.

## Histórias de Usuário

Persona principal: **candidato** que mantém o perfil e adapta o currículo para várias vagas.

1. Como candidato, eu quero que a leitura do meu currículo reconheça contexto, responsabilidades, realizações e skills, para não reorganizar o texto à mão.
2. Como candidato, eu quero que a IA complete os blocos que meu currículo não traz, para não partir de campos vazios.
3. Como candidato, eu quero editar os quatro blocos de cada experiência no perfil, para manter minha carreira organizada.
4. Como candidato, eu quero criar e excluir skills de uma experiência como tags, para ajustar sem editar texto corrido.
5. Como candidato, eu quero que as skills das experiências entrem nas tecnologias gerais, para não cadastrar a mesma tecnologia duas vezes.
6. Como candidato, eu quero que o currículo gerado e o adaptado tragam os quatro blocos, para entregar ao recrutador um padrão claro.
7. Como candidato com perfil antigo, eu quero migrar para o padrão novo revisando o resultado, para não perder meus dados.

Casos extremos:

- O currículo traz só uma descrição corrida: a IA divide o texto nos quatro blocos e gera o que faltar.
- O currículo traz alguns blocos (ex.: só "Technologies"): os reconhecidos são mantidos e os demais são gerados.
- Os rótulos vêm em português ou em outra grafia ("Responsabilidades", "Principais entregas"): o reconhecimento aceita equivalentes.
- Skill repetida na experiência, ignorando maiúsculas e minúsculas: não é criada de novo.
- Skill já existente nas tecnologias gerais: não é duplicada.
- Skill removida de uma experiência: continua nas tecnologias gerais, porque outras experiências ou o usuário podem usá-la.
- Experiência sem um dos blocos após edição do usuário: o PDF omite o bloco e o rótulo, sem linhas vazias.
- Experiência curta, sem informação suficiente: a IA gera ao menos um item por lista e um contexto de uma frase.

## Funcionalidades Principais

### 1. Modelo de experiência com quatro blocos

Requisitos funcionais:

1. Cada experiência do perfil deve ter empresa, cargo, período, contexto, lista de responsabilidades, lista de realizações e lista de skills.
2. O contexto deve ter de uma a três frases.
3. Responsabilidades e realizações devem ter de 3 a 5 itens cada, o mesmo limite das conquistas na adaptação (JOB-0042). Itens são frases curtas, no idioma do currículo, com verbo de ação.
4. As realizações devem citar o resultado medido quando houver dado.
5. Empresa, cargo e período devem ser preservados exatamente como na fonte.

### 2. Leitura do currículo inicial

Requisitos funcionais:

6. A leitura deve tentar reconhecer os quatro blocos de cada experiência por rótulos e estrutura, em português e inglês.
7. Todo bloco reconhecido deve ser mantido como está no texto, sem reescrita.
8. Para cada bloco não reconhecido, a IA deve gerar o conteúdo a partir da descrição, do cargo, da empresa e do período da experiência.
9. A IA pode propor métricas e contextos realistas para o setor e o papel da experiência (ex.: sistema bancário), preferindo sempre os dados da fonte.
10. O resultado deve ir para a tela de revisão do perfil, com aviso de que a IA pode ter estimado métricas e deve ser conferida antes de salvar.

### 3. Perfil e edição

Requisitos funcionais:

11. A tela do perfil deve mostrar, por experiência, os campos "Contexto", "Principais responsabilidades", "Principais realizações" e "Skills".
12. Responsabilidades e realizações devem aceitar um item por linha, ignorando linhas em branco.
13. Skills devem ser tags: o usuário cria uma digitando e confirmando (Enter ou vírgula) e exclui clicando na tag, como nas tecnologias do perfil (JOB-0041).
14. A ação "Sugestões de IA" por experiência deve devolver os quatro blocos novos a partir dos valores atuais, e o usuário aplica ou descarta.
15. Perfis antigos (descrição livre) devem ser migrados ao serem abertos: o sistema reconhece ou gera os blocos com a regra do item 6 ao 9, mostra o resultado e só salva quando o usuário confirmar.

### 4. Sincronia de skills com as tecnologias gerais

Requisitos funcionais:

16. Ao salvar o perfil, o sistema deve comparar as skills de todas as experiências com as tecnologias gerais.
17. A comparação deve ignorar maiúsculas, minúsculas e espaços extras.
18. Toda skill de experiência ausente nas tecnologias gerais deve ser incluída no fim da lista de tecnologias do perfil, que é uma lista simples, sem categorias e sem IA.
19. O usuário deve ver, após salvar, quais tecnologias foram incluídas.
20. Excluir uma skill de uma experiência não remove a tecnologia geral.

### 5. Currículo gerado e currículo adaptado

Requisitos funcionais:

21. O currículo gerado a partir do perfil deve trazer os quatro blocos de cada experiência.
22. Na adaptação a uma vaga, a IA pode reescrever os quatro blocos para aderência à vaga, com as regras de fidelidade e limites das JOB-0040, JOB-0042 e JOB-0043.
23. A tela de revisão do adaptado deve mostrar e permitir editar os quatro blocos, com skills em tags.
24. No currículo adaptado, as skills das experiências ausentes nas competências devem entrar na categoria "Tecnologias", e o usuário as reorganiza.
25. A ação "Avaliar" de cada experiência deve considerar os quatro blocos.

### 6. PDF e idioma

Requisitos funcionais:

26. O PDF deve apresentar, por experiência, nesta ordem: contexto, responsabilidades, realizações e skills.
27. O contexto aparece como parágrafo precedido do rótulo, as listas como bullets, e as skills em uma linha separada por " | ".
28. Os rótulos devem ser traduzidos conforme o idioma do currículo: em inglês "Context", "Key Responsibilities", "Key Achievements" e "Technologies"; em português "Contexto", "Principais responsabilidades", "Principais realizações" e "Tecnologias".
29. Bloco vazio não deve deixar rótulo solto nem linha vazia.
30. Currículos vindos de PDF direto (sem experiências estruturadas) devem receber o mesmo padrão no texto das experiências.

### 7. Organização das competências por arrastar e soltar

Requisitos funcionais:

31. Na revisão do currículo adaptado, o usuário deve poder arrastar uma tag para reordená-la dentro da categoria e movê-la para outra categoria.
32. Mover uma tag não deve duplicar a tag na categoria de destino (ignorando maiúsculas e minúsculas).
33. Categoria que ficar sem tags deve ser descartada ao salvar, como hoje.
34. A mesma ação deve funcionar pelo teclado, com anúncio do movimento para leitores de tela.

## Experiência do Usuário

Jornada de importação:

1. O usuário envia o currículo inicial.
2. O sistema mostra as experiências já separadas nos quatro blocos, com aviso de números e contextos que a IA pode ter estimado.
3. O usuário revisa, edita e salva. As skills novas entram nas tecnologias gerais e o sistema informa quais.

Requisitos de UI/UX:

- Mesmos componentes e mensagens de erro do cadastro de perfil e da revisão do adaptado.
- Tags de skills com o mesmo comportamento das tecnologias gerais.

Acessibilidade:

- Rótulos associados aos campos e anúncio das tags criadas e removidas.
- Retorno do foco ao campo após aplicar uma sugestão, como na JOB-0034.
- Contraste adequado do contexto e dos rótulos no PDF impresso.

## Restrições Técnicas de Alto Nível

- Arquitetura hexagonal: os quatro blocos fazem parte do modelo de domínio da experiência. As portas de IA devolvem esse modelo e o gerador de PDF o desenha.
- A sincronia das skills é regra de domínio, independente da interface.
- O perfil guarda os blocos de forma persistente (muda a decisão da JOB-0035). Perfis antigos continuam legíveis até a migração.
- A IA usa o provedor já configurado; sem novo provedor.
- Dados pessoais e textos do currículo não aparecem em logs.
- Não aumentar de forma relevante o tempo de geração (o aviso atual é de até 1 minuto). A leitura do currículo pode chamar a IA só para os blocos ausentes.
- Idiomas suportados: português e inglês.

## Fora de Escopo

- Marcar por item o que a IA estimou ou gerou no PDF.
- Dividir as tecnologias gerais do perfil em categorias.
- Remover tecnologias gerais automaticamente quando a skill some das experiências.
- Editor com formatação (negrito, itálico) ou subitens nas listas.
- Idiomas além de português e inglês.
- Importação direta do LinkedIn.
- Estruturar formação, certificações e idiomas.

## Questões em Aberto

1. **Realizações e banco de conquistas (JOB-0042):** o banco já guarda conquistas por experiência no perfil. Proposta: as "Principais realizações" e o banco são a mesma lista, sem duplicar dado. Confirma?
2. **Limite "mesmos do achievements":** interpretei como 3 a 5 itens (JOB-0042) para responsabilidades e realizações, e 1 a 3 frases para o contexto (JOB-0035). Está correto?
3. **Números estimados:** esta JOB amplia a geração de métricas e contextos pela IA, por decisão do produto. O aviso na revisão é a única proteção. Convém sinalizar por item em outra JOB?
4. **Resolvida:** a skill nova entra no fim da lista simples do perfil e, no adaptado, na categoria "Tecnologias". Sem sugestão de categoria pela IA.
5. **Migração de perfis antigos:** o usuário que nunca abrir o perfil continua com a descrição livre. Os fluxos de adaptação devem migrar na hora ou exigir a confirmação antes?

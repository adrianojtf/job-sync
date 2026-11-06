# Documento de Requisitos de Produto (PRD) — JOB-0035

## Visão Geral

Hoje a IA devolve cada experiência do currículo como um único texto de descrição. O resultado varia de uma adaptação para outra e não tem a estrutura que recrutadores esperam: poucas conquistas objetivas e uma frase que situa a empresa e o papel.

Este PRD define um padrão para cada experiência do currículo adaptado:

- **Conquistas (achievements):** lista de bullets, cada um com uma entrega e, quando possível, o resultado medido.
- **Contexto (context):** um parágrafo curto, depois dos bullets, que explica a empresa, a área e o papel. No PDF ele aparece em itálico e cinza, como no exemplo de referência.

Conquistas e contexto passam a ser **campos separados** de cada experiência. A IA os preenche na adaptação e nas sugestões por experiência, o usuário os edita na tela de revisão, e o PDF os desenha no padrão.

Analogia: hoje a IA entrega um parágrafo corrido. Com esta mudança, ela entrega uma ficha com duas partes fixas: "o que eu fiz" e "onde e em que cenário".

Este PRD depende da JOB-0033 (revisão do currículo adaptado) e da JOB-0034 (sugestões de IA por seção), ambas no PR de número 45.

## Objetivos

- Todo currículo adaptado traz as experiências no mesmo padrão: conquistas e contexto.
- O usuário edita conquistas e contexto separadamente antes do PDF.
- O PDF apresenta o contexto em itálico e cinza, depois dos bullets.
- As sugestões de IA por experiência mantêm o padrão.

Como medir o sucesso:

- 100% das experiências adaptadas pela IA a partir do perfil estruturado saem com ao menos uma conquista.
- Nenhuma sugestão de experiência na revisão desfaz o padrão.
- Nenhuma regressão na geração do PDF de currículos vindos de PDF.

## Histórias de Usuário

Persona principal: **candidato** que adapta o currículo mestre para uma vaga e revisa o resultado.

1. Como candidato, eu quero que cada experiência venha com conquistas em bullets, para que o recrutador leia resultados e não um parágrafo.
2. Como candidato, eu quero um parágrafo de contexto depois das conquistas, para situar a empresa e o meu papel.
3. Como candidato, eu quero editar as conquistas e o contexto em campos separados, para corrigir cada parte sem mexer na outra.
4. Como candidato, eu quero pedir uma sugestão de IA para uma experiência e receber conquistas e contexto novos, para refinar sem perder o padrão.
5. Como candidato, eu quero ser avisado de que a IA pode ter estimado números, para conferir antes de enviar o currículo.
6. Como candidato, eu quero ver o contexto destacado no PDF, para distingui-lo das conquistas.

Casos extremos:

- A fonte não traz resultado mensurável: o bullet sai sem número ou com uma estimativa conservadora, e o aviso de números estimados continua visível.
- A experiência tem um texto muito curto: a IA gera ao menos uma conquista e um contexto de uma frase.
- O usuário apaga o contexto: o PDF mostra só os bullets.
- O usuário apaga todas as conquistas e mantém o contexto: o PDF mostra só o contexto.
- Currículo vindo de PDF (sem experiências estruturadas): a IA também usa o padrão no texto da seção, e o PDF o desenha igual.

## Funcionalidades Principais

### 1. Experiência com conquistas e contexto

Requisitos funcionais:

1. Cada experiência do rascunho adaptado deve ter cargo, empresa, período, uma lista de conquistas e um contexto.
2. A IA deve gerar, para cada experiência, ao menos uma conquista e um contexto de uma a três frases.
3. As conquistas devem ser frases curtas, no idioma alvo, começando por verbo de ação e, quando houver dado, citando o resultado medido.
4. O contexto deve descrever a empresa, a área e o papel, sem repetir as conquistas.
5. Cargo, empresa e período devem ser preservados exatamente como no perfil.
6. A IA pode propor métricas e volumes plausíveis quando a fonte não os tiver, preferindo sempre os números da fonte quando existirem.

### 2. Revisão e edição

Requisitos funcionais:

7. Na tela de revisão, cada experiência deve ter os campos "Conquistas" e "Contexto", além de empresa, cargo e período.
8. O campo "Conquistas" deve aceitar uma conquista por linha, e linhas em branco devem ser ignoradas.
9. A tela deve avisar que a IA pode ter estimado métricas e volumes e que o usuário deve confirmá-los antes de gerar o PDF.
10. A ação "Avaliar" de cada experiência deve avaliar o texto formado por conquistas e contexto.

### 3. Sugestões de IA por experiência

Requisitos funcionais:

11. O botão "Sugestões de IA" de cada experiência na revisão deve devolver conquistas e contexto novos, a partir dos valores atuais dos dois campos.
12. A sugestão deve mostrar conquistas e contexto no painel e, ao aplicar, atualizar os dois campos.
13. Em "Meu perfil", o botão "Sugestões de IA" de cada experiência continua melhorando o texto livre de descrição, sem o padrão, porque o perfil não passa a guardar conquistas e contexto.

### 4. PDF

Requisitos funcionais:

14. O PDF deve listar as conquistas como bullets, na ordem informada.
15. O PDF deve exibir o contexto depois dos bullets, em itálico e cinza, precedido do rótulo "Context:" (idioma inglês) ou "Contexto:" (idioma português).
16. Experiência sem conquistas ou sem contexto não deve deixar linhas vazias nem rótulo solto no PDF.
17. Currículos vindos de PDF devem receber o mesmo padrão no texto da seção de experiências, e o PDF deve desenhá-lo da mesma forma.

### 5. Compatibilidade

Requisitos funcionais:

18. A API de adaptação com PDF direto e o app Streamlit devem continuar funcionando, e o PDF gerado por eles passa a usar o padrão novo.
19. O currículo mestre e a biblioteca de currículos não devem ser alterados.

## Experiência do Usuário

Jornada na revisão:

1. O usuário gera o currículo adaptado e chega à tela de revisão.
2. Vê um aviso: "A IA pode ter estimado métricas e volumes nas experiências. Confirme que os números são verdadeiros antes de gerar o PDF."
3. Em cada experiência, edita "Conquistas" (uma por linha) e "Contexto".
4. Opcionalmente clica em "Sugestões de IA" da experiência, vê conquistas e contexto sugeridos e aplica ou descarta.
5. Confirma, e o PDF sai com bullets e o contexto em itálico cinza.

Requisitos de UI/UX:

- Mesmos componentes e mensagens de erro da tela de cadastro, com os dois campos novos no lugar da descrição.
- Painel de sugestão com conquistas em lista e contexto em parágrafo, identificado como "Sugestão da IA".
- O aviso de números estimados fica no topo da revisão, não em cada experiência.

Acessibilidade:

- Rótulos associados e texto de ajuda nos campos ("Uma conquista por linha").
- Anúncio da sugestão e retorno do foco ao campo, como nas sugestões da JOB-0034.
- O contraste do cinza do contexto no PDF deve manter leitura confortável na impressão.

## Restrições Técnicas de Alto Nível

- Arquitetura hexagonal: conquistas e contexto fazem parte do modelo de domínio da experiência adaptada. As portas de IA devolvem esse modelo, e o gerador de PDF o desenha.
- Sem persistência nova: o rascunho continua só na sessão da tela.
- O perfil estruturado não muda (descrição em texto livre).
- A IA usa o provedor já configurado; sem novo provedor.
- Dados pessoais e textos do currículo não aparecem em logs.
- Os contratos da JOB-0033 e da JOB-0034 ainda não foram publicados. Por isso podem mudar nesta JOB sem impacto externo, desde que o PR 45 não tenha sido integrado a um ambiente.

## Fora de Escopo

- Guardar conquistas e contexto no currículo mestre ou na biblioteca.
- Editor com formatação (negrito, itálico) nos campos.
- Bullets com subitens.
- Lista dinâmica de conquistas com um campo por item (um campo de texto com uma linha por conquista basta nesta versão).
- Estruturar formação, certificações e idiomas.
- Indicar por experiência quais números foram estimados.
- Marcar o texto estimado visualmente no PDF.

## Questões em Aberto

1. **Números estimados:** a regra atual proíbe inventar métricas, e esta JOB a relaxa por decisão do produto. O aviso na revisão é a única proteção. Convém, em outra JOB, sinalizar por experiência o que foi estimado?
2. **Fonte PDF:** o padrão é aplicado como convenção de texto (linha "Context:"), porque não há campos estruturados nessa fonte. Se a IA não seguir a convenção, o PDF mostra a linha comum, sem itálico. Isso é aceitável?
3. **Quantidade de conquistas:** definir um mínimo e um máximo por experiência (proposta: de 2 a 6)? Hoje só exigimos ao menos uma.
4. **Idioma do rótulo:** o rótulo segue o idioma alvo ("Contexto:" ou "Context:"). Algum outro idioma além de português e inglês será suportado?

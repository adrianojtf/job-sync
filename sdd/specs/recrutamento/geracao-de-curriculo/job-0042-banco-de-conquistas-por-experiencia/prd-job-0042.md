# Documento de Requisitos de Produto (PRD) — JOB-0042

## Visão Geral

Hoje cada experiência do perfil tem um texto livre de descrição. A IA reescreve esse texto em "conquistas e contexto" a cada currículo adaptado (JOB-0035). As conquistas existem só dentro do texto gerado: não são guardadas, não têm origem registrada e não podem ser escolhidas conforme a vaga.

Este PRD cria o **banco de conquistas**: cada experiência do perfil passa a ter uma lista de conquistas guardadas, escritas ou aprovadas pelo usuário. Na adaptação do currículo, a IA escolhe de 3 a 5 conquistas por experiência, as mais aderentes à vaga, e as usa como base das conquistas e do contexto.

Analogia: o banco é um estoque de peças e cada vaga é uma vitrine. A IA escolhe as peças certas para a vitrine, sem fabricar peças novas.

Este PRD também prepara a JOB-0043 (perguntas de elucidação), que abastece o banco com conquistas novas.

Depende da JOB-0035 (padrão de conquistas e contexto) e da JOB-0037 (aderência à vaga).

## Objetivos

- O usuário guarda, por experiência, as conquistas que já viveu e as reaproveita em qualquer vaga.
- A adaptação do currículo usa de 3 a 5 conquistas por experiência, as mais aderentes à vaga.
- As conquistas escolhidas são fiéis ao que o usuário aprovou: a IA não acrescenta fato, número ou resultado.
- Perfis sem conquistas cadastradas continuam funcionando como hoje.

Como medir o sucesso:

- Em currículos adaptados de perfis com conquistas cadastradas, 100% das experiências com conquistas no banco saem com 3 a 5 conquistas (ou todas, se houver menos de 3).
- Em uma avaliação manual com ao menos duas vagas de áreas diferentes e o mesmo perfil, as conquistas escolhidas mudam conforme a vaga.
- Nenhuma conquista gerada traz fato, número ou resultado ausente do banco.
- Nenhuma regressão nos testes das JOB-0035, JOB-0037 e JOB-0040.

## Histórias de Usuário

Persona principal: **candidato** que mantém um perfil mestre e adapta o currículo para várias vagas.

1. Como candidato, eu quero cadastrar conquistas em cada experiência do meu perfil, para não reescrevê-las a cada vaga.
2. Como candidato, eu quero editar e excluir conquistas, para manter o banco atual e correto.
3. Como candidato, eu quero que a IA escolha de 3 a 5 conquistas por experiência conforme a vaga, para o currículo falar do que importa àquela posição.
4. Como candidato, eu quero que a IA não invente números nem resultados nas conquistas escolhidas, para eu defender cada linha em entrevista.
5. Como candidato, eu quero ser avisado quando uma conquista nova se parece com outra já guardada, para não duplicar o banco.
6. Como candidato, eu quero que experiências sem conquistas cadastradas continuem funcionando, para usar o sistema sem preencher tudo antes.

Casos extremos:

- Experiência com menos de 3 conquistas no banco: a adaptação usa todas e completa o padrão como hoje, a partir da descrição.
- Experiência sem nenhuma conquista no banco: a adaptação segue o comportamento atual, a partir da descrição.
- Nenhuma conquista do banco tem relação com a vaga: a IA escolhe as 3 mais próximas, sem forçar relação inexistente.
- Currículo vindo de PDF salvo (sem experiências estruturadas): o banco não se aplica, e o comportamento atual continua.
- Conquista excluída: não aparece em novas adaptações; currículos já salvos não mudam.

## Funcionalidades Principais

### 1. Banco de conquistas por experiência

Requisitos funcionais:

1. Cada experiência do perfil deve poder ter uma lista de conquistas guardadas.
2. O usuário deve poder cadastrar, editar e excluir conquistas de uma experiência no perfil.
3. Cada conquista deve guardar o texto aprovado pelo usuário e a origem (cadastro manual ou resposta às perguntas da JOB-0043).
4. A conquista salva pertence a uma experiência. Não existe conquista sem experiência.
5. Ao salvar uma conquista parecida com outra da mesma experiência, o sistema deve avisar o usuário e mostrar a existente, e o usuário decide entre salvar mesmo assim ou cancelar.
6. Perfis existentes não exigem migração: o banco começa vazio e a descrição atual da experiência continua válida.

### 2. Seleção na adaptação do currículo

Requisitos funcionais:

7. Na adaptação, para cada experiência com conquistas no banco, a IA deve escolher de 3 a 5, as mais aderentes à vaga e ao cargo-alvo, com a mais relevante primeiro.
8. A IA pode reescrever a redação de uma conquista escolhida para adequá-la à vaga, mas não pode acrescentar fato, número, resultado, tecnologia ou prática que a conquista não tenha.
9. A escolha deve valer para o padrão de conquistas e contexto da JOB-0035, sem mudar o formato do PDF.
10. O contexto da experiência pode usar as conquistas escolhidas como base, com a mesma regra de fidelidade.
11. Experiência com menos de 3 conquistas no banco usa todas, e o restante segue o comportamento atual a partir da descrição.
12. Experiência sem conquistas no banco segue o comportamento atual.
13. O botão "Sugestões de IA" de uma experiência na revisão deve respeitar as mesmas regras e partir das conquistas escolhidas.
14. A regra vale só para currículos adaptados a partir do perfil estruturado ("Meu perfil").

### 3. Manutenção do banco

Requisitos funcionais:

15. O banco deve ser simples de revisar: lista por experiência, com edição e exclusão diretas.
16. Excluir uma conquista não altera currículos adaptados já salvos.
17. Não há limite rígido de conquistas por experiência no banco. O limite de 3 a 5 vale para o uso na adaptação.

## Experiência do Usuário

Fluxo principal:

1. Em "Meu perfil", o usuário abre uma experiência e vê a lista de conquistas.
2. Cadastra uma conquista. Se ela se parecer com outra, vê um aviso com a conquista existente.
3. Gera um currículo adaptado a uma vaga. A IA escolhe as conquistas de cada experiência.
4. Na revisão, edita o que quiser, como hoje, e gera o PDF.

Requisitos de UX:

- O aviso de revisão existente ("Confirme que você consegue defender em entrevista o que a IA ajustou") continua visível.
- Acessibilidade: campos e avisos acessíveis por teclado e leitor de tela, como no restante do perfil.

## Restrições Técnicas de Alto Nível

- Usar o provedor de IA e o fluxo de adaptação existentes, sem novo serviço externo.
- Não aumentar de forma relevante o tempo de geração do currículo (o aviso atual é de até 1 minuto).
- Privacidade: as conquistas são dados do perfil e são enviadas ao provedor de IA como o restante do perfil.
- Compatibilidade: perfis e currículos salvos antes desta entrega continuam abrindo sem alteração.

## Fora de Escopo

- Perguntas de elucidação ao usuário (JOB-0043).
- Importar automaticamente conquistas a partir da descrição atual da experiência.
- Conquistas globais, sem experiência associada.
- Busca por similaridade em larga escala, enquanto o banco couber no contexto da IA.
- Mudar o formato ou o layout do PDF.
- Validação automática, em tempo de execução, de números ou fatos nas conquistas escolhidas.

## Questões em Aberto

1. O cadastro manual entra na primeira versão (decisão tomada: sim), para que o banco funcione sem esperar a JOB-0043. Confirmar o fluxo de tela na techspec.
2. Quando o banco de uma experiência ficar grande, a IA recebe todas as conquistas? Resolvida por ora: sem teto, com 8 conquistas a latência foi de cerca de 4,8 s por experiência. Reavaliar acima de cerca de 20 conquistas.
3. Resolvida: comparação textual no domínio (limite de similaridade 0,6). Paráfrases com palavras reordenadas podem passar; o aviso é só informativo.
4. Faz sentido oferecer, depois, a criação de conquistas a partir da descrição atual da experiência? Fica para uma entrega futura, se houver demanda.

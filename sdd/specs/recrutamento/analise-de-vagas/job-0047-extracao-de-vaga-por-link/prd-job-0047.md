# Documento de Requisitos de Produto (PRD)

## Visão Geral

Hoje, para adaptar um currículo a uma vaga, a pessoa precisa copiar a descrição da vaga, colá-la na tela e digitar cargo e empresa à mão. Na captura de vagas, a única entrada é o texto. Isso consome tempo e gera erros.

Esta funcionalidade permite informar o **link da vaga** (principalmente do LinkedIn) e ter os dados da vaga preenchidos automaticamente: cargo, empresa, local e descrição. A pessoa revisa os dados e segue o fluxo normal. Quando o link não puder ser lido, o sistema oferece a alternativa de colar o texto da vaga, com preenchimento automático dos campos a partir desse texto.

A funcionalidade vale para duas telas: "Ajustar currículo para vaga" e "Captura de vagas".

## Objetivos

- Reduzir o esforço de entrada de uma vaga para um passo: colar o link e conferir os campos.
- Preencher corretamente cargo, empresa e descrição em vagas de links suportados, com revisão da pessoa antes de usar.
- Nunca deixar a pessoa sem saída: toda falha de leitura leva a uma alternativa clara.
- Guardar a descrição fiel ao original, sem resumo, para não perder palavras-chave usadas na adaptação e na análise ATS.

Indicadores de sucesso:
- Percentual de links colados que resultam em campos preenchidos sem ajuste manual.
- Percentual de links que caem no fallback de colar texto.
- Tempo médio entre colar o link e ter os campos preenchidos.

## Histórias de Usuário

1. Como pessoa candidata, eu quero colar o link de uma vaga do LinkedIn em "Ajustar currículo para vaga" para que cargo, empresa e descrição sejam preenchidos sem eu copiar e digitar.
2. Como pessoa candidata, eu quero colar o link na tela de captura de vagas para guardar a vaga com a origem registrada.
3. Como pessoa candidata, eu quero revisar e corrigir os campos preenchidos antes de adaptar o currículo, para não usar dados errados.
4. Como pessoa candidata, quando o sistema não conseguir ler o link, eu quero entender o motivo e poder colar o texto da vaga, para continuar mesmo assim.
5. Como pessoa candidata, eu quero colar um link com parâmetros de rastreamento (por exemplo, vindo de um e-mail do LinkedIn) e ter o link tratado corretamente.
6. Como pessoa candidata, eu quero usar links de outros sites de vagas (Gupy, Greenhouse, Lever, páginas de carreira) e receber o mesmo preenchimento, quando o site permitir a leitura.

Casos extremos:
- Link inválido, vaga removida ou encerrada.
- Link do LinkedIn que aponta para uma busca e não para uma vaga.
- Vaga com descrição em outro idioma.
- Link e texto informados ao mesmo tempo.

## Funcionalidades Principais

### 1. Campo "Link da vaga"

Aceita o endereço de uma vaga e dispara a leitura dos dados. Está presente em "Ajustar currículo para vaga" e em "Captura de vagas".

Requisitos funcionais:
1. As telas "Ajustar currículo para vaga" e "Captura de vagas" devem oferecer o campo "Link da vaga".
2. O campo deve aceitar somente endereços `http` e `https` e informar erro claro para entradas inválidas.
3. A entrada manual por texto deve continuar disponível, como hoje.
4. Se o link e o texto forem informados juntos, o texto informado pela pessoa tem prioridade.

### 2. Normalização do link

Requisitos funcionais:
5. O sistema deve remover do link parâmetros de rastreamento e sessão antes de usá-lo ou salvá-lo.
6. Para o LinkedIn, o sistema deve reconhecer o identificador da vaga tanto em links diretos quanto em links de busca que indicam a vaga selecionada (por exemplo, com `currentJobId`).
7. A URL salva como origem da vaga deve ser a versão normalizada.
8. Se o link do LinkedIn não identificar uma vaga específica, o sistema deve informar isso e orientar a pessoa.

### 3. Extração dos dados da vaga

Requisitos funcionais:
9. O sistema deve extrair: cargo, empresa, local e descrição completa.
10. O sistema deve extrair, quando disponíveis: tipo de contratação, senioridade e setor.
11. A descrição deve ser mantida no idioma e no conteúdo originais, preservando a estrutura de listas e parágrafos. O sistema não deve resumir nem traduzir.
12. Dados de contexto sem valor para a adaptação, como número de candidatos e tempo desde a publicação, não devem ser guardados.
13. Para sites diferentes do LinkedIn, o sistema deve tentar a leitura da página e extrair os mesmos campos, quando o site permitir.
14. Quando os campos não puderem ser obtidos de forma estruturada, o sistema deve extrair os campos a partir do texto da página.

### 4. Alternativa quando a leitura falha

Requisitos funcionais:
15. Se a leitura falhar (bloqueio do site, página que exige login, vaga encerrada, tempo esgotado), o sistema deve exibir uma mensagem que explique o motivo em linguagem simples.
16. A mensagem deve oferecer colar o texto da vaga como alternativa.
17. Ao colar o texto, o sistema deve extrair e preencher cargo, empresa, local e descrição a partir dele, usando o mesmo fluxo de revisão.
18. Uma falha de leitura nunca deve impedir a pessoa de concluir o fluxo.

### 5. Revisão antes de usar

Requisitos funcionais:
19. Os campos preenchidos devem ser editáveis e tratados como rascunho. Nada é salvo nem usado para adaptação antes da confirmação da pessoa.
20. O sistema deve indicar quais campos foram preenchidos automaticamente e quais ficaram vazios.

### 6. Captura de vagas com link

Requisitos funcionais:
21. Na captura, a vaga lida pelo link deve ser exibida como rascunho para confirmação antes de ser salva.
22. A vaga salva deve registrar a URL normalizada como origem.
23. Cargo e empresa extraídos devem poder ser guardados junto à vaga (decisão em Questões em Aberto).

## Experiência do Usuário

Persona: pessoa candidata que se candidata a várias vagas e adapta o currículo para cada uma.

Fluxo principal:
1. A pessoa abre a vaga no LinkedIn e copia o link.
2. Cola no campo "Link da vaga".
3. O sistema mostra "Lendo a vaga..." e, em poucos segundos, preenche os campos.
4. A pessoa confere, ajusta o que for necessário e segue para adaptar o currículo.

Fluxo alternativo: ao falhar, a tela mostra o motivo e um campo para colar o texto da vaga.

Requisitos de UX e acessibilidade:
- Indicador de progresso e botão para cancelar a leitura.
- Mensagens de erro e de estado anunciadas a leitores de tela.
- Campo operável somente por teclado.
- Texto de apoio explicando que, para alguns sites, pode ser necessário colar o texto.

## Restrições Técnicas de Alto Nível

- **Fonte no LinkedIn:** a leitura usa somente a versão pública da vaga, visível a visitantes sem login. O sistema não pede nem armazena credenciais do LinkedIn. O login com LinkedIn (OAuth) não dá acesso a vagas e está fora desta funcionalidade.
- **Sem contornar proteções:** o sistema não deve usar rotação de IP, falsificação de navegador, resolução de desafios anti-bot nem contas de terceiros. Se o site bloquear (por exemplo, resposta 429 ou desafio), o sistema para e oferece a alternativa.
- **Uso moderado:** uma consulta por link informado pela pessoa, sem varredura, busca em lote nem repetição automática após bloqueio.
- **Segurança (SSRF):** como o servidor passa a buscar endereços informados por usuários, o sistema deve recusar endereços internos (`localhost`, redes privadas, metadados de nuvem), limitar redirecionamentos, tamanho da resposta e tempo, e aceitar apenas `http` e `https`.
- **Desempenho:** tempo máximo de 15 segundos por leitura, com mensagem de erro ao exceder.
- **Privacidade:** não guardar dados pessoais de terceiros que apareçam na página (nomes de recrutadores, candidatos). Registrar em log apenas o domínio, o resultado (sucesso ou falha) e o motivo, sem o conteúdo da vaga.
- **Custo:** a extração por texto usa o provedor de IA já configurado no projeto, com limite de tamanho do texto enviado.
- **Desligável:** a leitura de links do LinkedIn deve poder ser desativada por configuração, sem afetar os demais sites nem a entrada manual.
- **Risco de termos de uso:** os termos do LinkedIn proíbem o acesso automatizado. O risco é aceito pelo responsável pelo produto e fica registrado como decisão. Esta funcionalidade não garante que o LinkedIn continuará permitindo a leitura.
- **Arquitetura:** respeitar a arquitetura hexagonal e o DDD do projeto. Os detalhes de implementação ficam na Tech Spec.

## Critérios de Aceitação

1. Dado um link público direto de vaga do LinkedIn, quando a pessoa o cola em "Ajustar currículo para vaga", então cargo, empresa, local e descrição são preenchidos e editáveis.
2. Dado um link com parâmetros de rastreamento, então a URL usada e salva está sem esses parâmetros.
3. Dado um link do LinkedIn de busca com a vaga selecionada, então o sistema identifica a vaga correta ou informa que não foi possível.
4. Dado um link que o site bloqueia, então a pessoa vê o motivo e a opção de colar o texto, e consegue concluir o fluxo.
5. Dado um texto colado, então os campos são preenchidos a partir dele e a revisão é a mesma do fluxo por link.
6. Dado um link e um texto informados juntos, então o texto prevalece.
7. Dado um endereço interno (`localhost` ou IP privado), então o sistema o recusa sem fazer a requisição.
8. Dada uma vaga com descrição em português, então a descrição salva permanece em português e sem resumo.
9. Na captura, dado um link lido com sucesso, então a vaga só é salva após a confirmação e com a URL normalizada.
10. Dada a leitura do LinkedIn desativada por configuração, então o campo informa que o link do LinkedIn não é suportado e oferece colar o texto.
11. Dado um tempo de leitura acima de 15 segundos, então a pessoa recebe mensagem de erro e a alternativa.

## Fora de Escopo

- Extensão de navegador para ler vagas (decisão do produto: não será usada para esta funcionalidade).
- Login com LinkedIn (Auth0 ou OAuth) para ler vagas.
- Uso de contas, cookies ou sessões do LinkedIn do usuário ou de terceiros.
- Contorno de proteções anti-bot ou do bloqueio por IP.
- Contratação de provedor externo de scraping (avaliado como alternativa futura).
- Coleta em lote, monitoramento ou busca de vagas no LinkedIn.
- Tradução ou resumo automático da descrição da vaga.
- Candidatura automática ou preenchimento de formulários de terceiros.
- Dados do funil de candidatura do usuário (status, datas de entrevista), tratados em outro PRD.

## Questões em Aberto

1. **Código Jira:** `job-0047` é uma proposta (o último código no repositório é `job-0046`). Confirmar ou informar outro.
2. **Bloqueio em produção:** o teste de leitura sem login funcionou a partir de uma máquina residencial. IPs de servidor podem ser bloqueados com mais frequência. É preciso medir a taxa de sucesso em produção e definir o limite aceitável antes de manter a funcionalidade.
3. **Alternativa futura:** se a taxa de sucesso for baixa, avaliar um provedor pago de scraping, com custo por consulta.
4. **Modelo de dados da vaga:** guardar cargo, empresa e local na vaga capturada exige mudança no modelo atual, que hoje guarda só texto e URL de origem. Confirmar se entra neste PRD.
5. **Sites suportados:** definir quais sites além do LinkedIn entram no MVP (Gupy, Greenhouse, Lever, páginas de carreira) e qual taxa de sucesso é esperada em cada um.
6. **Limite de uso:** definir um limite diário de leituras por perfil para evitar abuso e reduzir o risco de bloqueio.
7. **Custo de IA:** estimar o custo por extração baseada em texto e definir o limite de tamanho do texto enviado.
8. **Campos secundários:** confirmar se tipo de contratação, senioridade e setor são exibidos ou apenas guardados.
9. **Vaga encerrada:** definir a mensagem e o tratamento para vagas que não aceitam mais candidaturas.

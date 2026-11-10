# Documento de Requisitos de Produto (PRD)

## Visão Geral

O login atual (job-0004) identifica a pessoa apenas por um texto livre, sem senha. Quem souber o identificador de outra pessoa acessa o perfil dela, os currículos salvos e as candidaturas. Isso serviu para 2-4 pessoas de confiança, mas bloqueia qualquer uso além desse grupo.

Este PRD define a V2 do login (issue #13): autenticação real, com **entrada via conta Google** ou **entrada via e-mail e senha**, e **um perfil por usuário**. Os dois caminhos devem ter o mesmo nível de segurança. O app aceita **qualquer conta Google** (Gmail e Google Workspace), o que o Google chama de aplicativo multi-tenant. O isolamento continua por usuário: cada pessoa vê apenas os próprios dados.

Analogia: hoje o prédio tem porteiro que confere apenas o nome dito em voz alta. A V2 passa a conferir um documento, e o mesmo rigor vale para quem usa o crachá do Google e para quem usa o cadastro próprio.

## Objetivos

- Impedir que uma pessoa acesse o perfil de outra sem provar quem é.
- Permitir entrada com Google ou com e-mail e senha, com o mesmo nível de segurança.
- Preservar os perfis existentes (currículos, perfil estruturado, candidaturas) sem perda de dados.
- Deixar a integração com provedores de identidade preparada para novos provedores além do Google.
- Sucesso é: o dono de um perfil legado entra com Google, vê todos os dados anteriores, e uma segunda pessoa não consegue acessar esses dados.

Métricas a acompanhar:

- Percentual de logins concluídos com sucesso, por método (Google e e-mail/senha).
- Número de perfis legados vinculados a uma conta autenticada.
- Número de tentativas de login bloqueadas por excesso de falhas.

## Histórias de Usuário

1. Como usuário, quero entrar com minha conta Google para não criar nem lembrar mais uma senha.
2. Como usuário, quero me cadastrar e entrar com e-mail e senha quando não quiser usar o Google.
3. Como usuário com cadastro por e-mail, quero confirmar que o e-mail é meu antes de usar a conta.
4. Como usuário, quero recuperar o acesso caso esqueça a senha.
5. Como dono de um perfil legado, quero que minha conta autenticada seja vinculada ao perfil existente para não perder meus currículos e candidaturas.
6. Como usuário, quero que apenas eu veja meus dados, mesmo que outra pessoa conheça meu e-mail ou antigo identificador.
7. Como usuário, quero sair da aplicação e ter a sessão encerrada.
8. Como mantenedor, quero adicionar um novo provedor de identidade no futuro sem reescrever o fluxo de login.

Personas:

- **Usuário atual (2-4 pessoas):** já tem perfil com dados e precisa mantê-los.
- **Usuário novo:** chega sem perfil e espera entrar rápido, sem fricção.
- **Mantenedor (Adriano):** administra a migração dos perfis existentes e configura o provedor.

## Funcionalidades Principais

### 1. Login com Google

- O usuário clica em "Entrar com Google", autentica na tela do Google e volta logado.
- Qualquer conta Google pode entrar (Gmail e Workspace).
- O e-mail só é aceito como identidade se o Google informar que ele está verificado.

Requisitos funcionais:

1. O sistema deve oferecer entrada com conta Google a qualquer conta Google com e-mail verificado.
2. O sistema deve criar um perfil novo na primeira entrada de uma conta Google sem perfil associado.
3. O sistema deve recusar a entrada quando o Google não confirmar o e-mail como verificado.
4. O sistema deve exibir mensagem clara quando o usuário cancelar a autenticação ou o Google retornar erro.

### 2. Login com e-mail e senha

- O usuário se cadastra com e-mail e senha e entra com essas credenciais.
- A conta só fica ativa depois da confirmação do e-mail.
- Existe fluxo de recuperação de senha.

Requisitos funcionais:

5. O sistema deve permitir cadastro com e-mail e senha.
6. O sistema deve exigir confirmação do e-mail antes de liberar o acesso aos dados.
7. O sistema deve permitir a recuperação de senha por link enviado ao e-mail cadastrado.
8. O sistema deve limitar tentativas de login com falha e bloquear temporariamente o excesso.
9. O sistema não deve revelar, nas mensagens de erro, se um e-mail está ou não cadastrado.

### 3. Perfil único por usuário e vínculo de métodos

- Cada pessoa tem exatamente um perfil, identificado pelo e-mail verificado.
- Se a mesma pessoa usar Google e e-mail/senha com o mesmo e-mail verificado, ambos levam ao mesmo perfil.

Requisitos funcionais:

10. O sistema deve manter um único perfil por e-mail verificado.
11. O sistema deve vincular automaticamente um método de entrada a um perfil existente apenas quando o e-mail estiver verificado por esse método.
12. O sistema não deve vincular uma conta com e-mail não verificado a um perfil existente.

### 4. Migração dos perfis existentes

- O mantenedor registra o e-mail de cada perfil legado.
- No primeiro login autenticado com esse e-mail verificado, o sistema vincula a conta ao perfil legado.
- Os dados do perfil (currículos, perfil estruturado, candidaturas, token de captura) permanecem associados ao mesmo perfil.

Requisitos funcionais:

13. O sistema deve permitir ao mantenedor associar um e-mail a um perfil legado, sem alterar os dados do perfil.
14. O sistema deve vincular o perfil legado à conta autenticada no primeiro login com o e-mail associado, desde que verificado.
15. O sistema não deve permitir que um perfil legado seja reivindicado por quem não prove ser dono do e-mail associado.
16. Perfis legados sem e-mail associado devem permanecer inacessíveis por login até serem associados, e não devem ser apagados.

### 5. Sessão e logout

Requisitos funcionais:

17. O sistema deve manter o usuário autenticado entre recarregamentos da página enquanto a sessão for válida.
18. O sistema deve expirar a sessão após período de inatividade definido.
19. O sistema deve permitir logout, encerrando a sessão imediatamente.
20. O sistema deve negar acesso a qualquer dado de perfil para requisições sem sessão válida.
21. O sistema deve impedir que um usuário acesse dados de outro perfil, mesmo informando o identificador de outro perfil.

### 6. Extensibilidade de provedores

Requisitos funcionais:

22. O sistema deve tratar o Google como um provedor entre possíveis outros, de modo que adicionar um provedor não exija mudar as regras de perfil e vínculo.

### 7. Login simples legado

Requisitos funcionais:

23. O login simples por identificador não deve ficar disponível ao usuário final. Pode existir apenas em ambiente de desenvolvimento e testes, controlado por configuração.

## Experiência do Usuário

Jornada principal:

1. O usuário abre a aplicação e vê a tela de entrada com as opções "Entrar com Google" e "Entrar com e-mail e senha", mais o link de cadastro.
2. Com Google: autentica no Google e retorna logado, no próprio perfil.
3. Com e-mail: informa credenciais; se for o primeiro acesso, confirma o e-mail pelo link recebido.
4. O usuário legado entra uma vez com o e-mail associado e encontra seus dados anteriores.
5. Em qualquer tela autenticada, o usuário vê quem está logado e pode sair.

Considerações:

- Mensagens de erro em português, objetivas e sem expor detalhes que ajudem um atacante.
- A tela de entrada substitui a atual (`features/entrar`); as demais telas passam a exigir sessão.
- Acessibilidade: navegação por teclado e rótulos nos campos, no nível já adotado pelo frontend.

## Restrições Técnicas de Alto Nível

- **Protocolo:** OAuth 2.0 / OpenID Connect com Authorization Code e PKCE, conduzido pelo backend.
- **Sessão:** cookie HttpOnly, sem expor credenciais ao JavaScript do navegador.
- **Segurança igual nos dois métodos:** senha armazenada apenas como hash forte, verificação de e-mail, limite de tentativas, proteção contra CSRF e sessões com expiração.
- **Ambiente:** hoje frontend e API rodam na mesma origem, em máquina local. Em produção serão origens separadas. A solução não deve impedir essa evolução, mas separar origens não faz parte desta entrega.
- **Dados pessoais:** guardar o mínimo necessário do Google (identificador do provedor e e-mail verificado). Não registrar senhas, tokens ou códigos em log.
- **Envio de e-mail:** o cadastro e a recuperação de senha dependem de um canal de envio de e-mail. Em ambiente local, deve ser possível testar sem provedor real.
- **Persistência:** PostgreSQL, conforme job-0039. Preservar a Arquitetura Hexagonal e a organização por domínios (job-0036).
- **Configuração:** o app OAuth no Google Cloud deve aceitar qualquer conta Google. As credenciais ficam em variáveis de ambiente, nunca no repositório.

## Fora de Escopo

- Isolamento de dados por organização ou workspace (tenant como grupo de usuários), papéis e convites.
- Provedores além do Google (apenas a estrutura para adicioná-los).
- MFA próprio, login sem senha por link mágico e chaves de acesso (passkeys).
- Logout em todos os dispositivos, tela de gestão de conta e exclusão de conta (LGPD).
- Alterações na extensão Chrome. O token de captura existente deve continuar funcionando, associado ao mesmo perfil.
- Separação de origens entre frontend e API em produção.
- Lista de permissão (allowlist) de e-mails ou domínios.

## Questões em Aberto

Itens abaixo assumidos por recomendação, por falta de resposta. Confirmar ou corrigir:

1. **Método por e-mail:** assumi e-mail e senha. Se a intenção for código ou link enviado por e-mail (sem senha), os requisitos 5 a 9 mudam.
2. **Abertura do cadastro:** assumi que qualquer pessoa pode se cadastrar, sem allowlist nem convite.
3. **Login simples legado:** assumi que fica apenas em dev/teste, atrás de configuração (RF 23).
4. **Extensão e token de captura:** assumi que ficam fora de escopo e continuam funcionando.
5. **Política de senha** (tamanho mínimo, lista de senhas comuns) e **prazos** (expiração da sessão, validade dos links de confirmação e recuperação).
6. **Perfil legado sem e-mail:** o bloqueio do RF 16 é aceitável, ou deve existir outra forma de reivindicação?
7. **Conflito de e-mails:** se o e-mail do Google diferir do e-mail associado ao perfil legado, o mantenedor precisa corrigir manualmente?
8. **Troca de e-mail no Google:** como tratar o usuário que muda o e-mail da conta Google depois do vínculo?

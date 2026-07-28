# Documento de Requisitos de Produto (PRD)

## Visão Geral

O job-sync hoje é uma ferramenta *stateless*: o usuário sobe um PDF, cola uma descrição de vaga, recebe um currículo adaptado e tudo é esquecido no momento seguinte. Não há login, não há perfil, não há histórico. Isso bloqueia qualquer funcionalidade que dependa de continuidade — ATS score comparativo, tracker de candidaturas, múltiplas versões de currículo — porque não existe um "dono" para esses dados persistirem.

Este PRD define a fundação do produto: um login simples (sem senha, adequado ao contexto de uso pessoal/portfólio entre 2-4 pessoas), um perfil por pessoa, e a capacidade de salvar e reutilizar até 10 currículos por perfil. É a fase que todas as demais (ATS score, kanban de candidaturas, busca de vagas, preparação de entrevista) dependem para existir.

## Objetivos

- Permitir que cada pessoa tenha um espaço próprio e identificável dentro da aplicação.
- Eliminar a perda de contexto entre sessões: currículos enviados uma vez ficam disponíveis depois.
- Preparar a base de dados (perfil, currículo) que as fases seguintes vão estender (vaga, candidatura, entrevista).
- Sucesso é: um usuário consegue fechar o navegador, voltar no dia seguinte, entrar com o mesmo identificador e encontrar os currículos que salvou.

## Histórias de Usuário

1. Como usuário, eu quero entrar na aplicação com um identificador simples (sem precisar cadastrar senha) para acessar meu espaço pessoal rapidamente.
2. Como usuário, eu quero fazer upload de um currículo em PDF e salvá-lo no meu perfil para não precisar reenviar o mesmo arquivo toda vez que for adaptar para uma nova vaga.
3. Como usuário, eu quero ver a lista dos currículos que já salvei, com nome e data de envio, para escolher qual usar em uma nova adaptação.
4. Como usuário, eu quero ser avisado quando eu tentar salvar um 11º currículo, para saber que preciso remover algum antes de continuar.
5. Como usuário, eu quero poder remover um currículo salvo que não uso mais.

## Funcionalidades Principais

### 1. Login simples por identificador

- Tela inicial pede um identificador de usuário (ex: nome ou apelido); não há senha.
- Se o identificador já existe, carrega o perfil existente; se não existe, cria um novo perfil automaticamente.
- A sessão permanece ativa enquanto o navegador estiver aberto (sem necessidade de "lembrar-me" complexo).

Requisitos funcionais:
1. O sistema deve apresentar uma tela de entrada solicitando um identificador de usuário antes de liberar acesso ao restante da aplicação.
2. O sistema deve criar um novo perfil automaticamente na primeira vez que um identificador é usado.
3. O sistema deve carregar o perfil e os dados associados (currículos salvos) ao reconhecer um identificador já existente.
4. O sistema não deve exigir senha, e-mail ou qualquer outro dado de autenticação além do identificador.

### 2. Upload e biblioteca de currículos por perfil

- O usuário pode enviar um PDF de currículo e salvá-lo associado ao seu perfil, com um nome de referência (ex: "Currículo Backend Sênior").
- A biblioteca lista os currículos salvos com nome de referência e data de upload, permitindo selecionar um para reutilizar em uma nova adaptação (Fase 1 em diante) em vez de reenviar o arquivo.
- Limite de 10 currículos salvos por perfil; ao atingir o limite, o sistema bloqueia novos uploads até que algum seja removido.

Requisitos funcionais:
5. O sistema deve permitir salvar um PDF de currículo associado ao perfil ativo, com um nome de referência definido pelo usuário.
6. O sistema deve listar os currículos salvos do perfil ativo, ordenados por data de upload (mais recente primeiro).
7. O sistema deve impedir o salvamento de um 11º currículo enquanto o perfil tiver 10 currículos ativos, exibindo mensagem explicando o limite.
8. O sistema deve permitir a remoção de um currículo salvo pelo próprio usuário.
9. O sistema deve permitir selecionar um currículo já salvo como entrada para uma nova adaptação, sem exigir novo upload do mesmo arquivo.

## Experiência do Usuário

Personas:
- Usuário único de portfólio pessoal: entra ocasionalmente, quer o mínimo de fricção possível para testar e usar a ferramenta.
- Pequeno grupo de 2-4 pessoas testando o mesmo ambiente: cada um precisa do próprio espaço isolado, sem ver dados dos outros.

Jornada principal:
1. Usuário abre a aplicação, informa seu identificador na tela de entrada.
2. Se é a primeira vez, cai direto em um perfil vazio; se já usou antes, vê sua biblioteca de currículos salvos.
3. Usuário faz upload de um novo currículo ou seleciona um já salvo para seguir para a adaptação (fluxo já existente da Fase atual do MVP).
4. Usuário pode a qualquer momento voltar à biblioteca para gerenciar (adicionar/remover) currículos salvos.

Não há requisitos de acessibilidade além dos já suportados pelo Streamlit por padrão.

## Restrições Técnicas de Alto Nível

- Não deve introduzir dependência de serviços de autenticação de terceiros (OAuth, SSO) — identificador simples e local é suficiente para o contexto de uso.
- Os PDFs de currículo salvos devem ser armazenados de forma associada ao perfil, sem exposição entre perfis diferentes.
- A solução deve funcionar em ambiente local (mesmo modelo de execução atual do MVP, `streamlit run`), sem exigir infraestrutura de nuvem.
- Deve preservar a Arquitetura Hexagonal já adotada: a lógica de perfil e persistência de currículo não deve vazar para a camada de domínio como dependência de banco de dados.

## Fora de Escopo

- Autenticação real com senha, e-mail de verificação ou recuperação de conta.
- Edição de conteúdo do currículo diretamente na aplicação (o PDF salvo é sempre o arquivo original enviado).
- Compartilhamento de currículos ou perfis entre usuários.
- Qualquer tela de configurações de conta além do identificador de entrada.
- Exportação/backup de dados do perfil.

## Questões em Aberto

- O identificador de usuário precisa de alguma validação de formato (ex: só letras/números) ou aceita qualquer texto livre?
- Se dois usuários digitarem o mesmo identificador por coincidência, isso é aceitável (ambiente de confiança, uso pessoal) ou precisa de algum aviso?
- Currículos salvos devem ter algum prazo de expiração/limpeza automática, ou ficam indefinidamente até remoção manual?

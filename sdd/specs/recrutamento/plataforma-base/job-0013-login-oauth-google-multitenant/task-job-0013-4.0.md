# Tarefa 4.0: Serviços de sessão e de e-mail/senha

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar os casos de uso do login por e-mail e senha e do ciclo de vida da sessão, usando fakes das portas. Complexidade: high.

<requirements>
- `CadastrarUsuario`: resposta idêntica para e-mail novo e já existente; cria `Usuario` e `Perfil` (`u-` + 12 hex) para e-mail novo; aproveita `Usuario` pré-criado pelo mantenedor (sem credencial); envia confirmação.
- `ConfirmarEmail`: token de uso único, validade de 24 h; marca `email_verificado`.
- `EntrarComSenha`: erro genérico para e-mail desconhecido e senha errada (com verificação de hash fictício para igualar o tempo); `email_nao_confirmado` só depois de senha correta; cria sessão.
- `SolicitarRedefinicaoSenha`: resposta sempre igual; link com validade de 1 h.
- `RedefinirSenha`: token de uso único; troca o hash e apaga todas as sessões do usuário.
- `ResolverSessao`: valida expiração por inatividade (7 dias) e absoluta (30 dias), renova `ultimo_acesso_em` com limite de frequência.
- `EncerrarSessao`.
- Limite de tentativas: 5 falhas em 15 minutos bloqueiam por e-mail e por IP (`LimiteTentativasExcedido`).
- Prazos configuráveis por variáveis de ambiente, com esses valores como padrão.
</requirements>

## Subtarefas

- [ ] 4.1 `CadastrarUsuario` e `ConfirmarEmail` (testes primeiro).
- [ ] 4.2 `EntrarComSenha` com limite de tentativas.
- [ ] 4.3 `SolicitarRedefinicaoSenha` e `RedefinirSenha`.
- [ ] 4.4 `ResolverSessao` e `EncerrarSessao`.
- [ ] 4.5 Logs estruturados (INFO e WARNING) conforme "Monitoramento e Observabilidade".

## Detalhes de Implementação

Ver "Visão Geral dos Componentes", "Decisões Principais" e "Monitoramento" em `techspec-job-0013.md`. Estrutura `service_layer/<caso_de_uso>/service.py`, como em `perfil/service_layer/entrar_ou_criar_perfil/`. Relógio injetado.

## Critérios de Sucesso

- Todos os cenários da seção "Testes Unidade" da Tech Spec para estes serviços passam.
- Nenhum log contém senha, token ou e-mail completo.

## Testes da Tarefa

- [ ] Testes de unidade com fakes e relógio controlado

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/autenticacao/service_layer/*/service.py`
- `src/jobsync/tests/autenticacao/`

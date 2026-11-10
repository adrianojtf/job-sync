# Tarefa 5.0: Serviços do fluxo Google (`IniciarLoginOAuth`, `ConcluirLoginOAuth`)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o início e a conclusão do login via provedor de identidade, incluindo a regra de vínculo por e-mail verificado. Complexidade: high.

<requirements>
- `IniciarLoginOAuth`: gera `state`, `nonce` e `code_verifier`; grava o hash do `state` em `estado_oauth` (validade de 10 min); devolve a URL de autorização e o valor do cookie `js_oauth`.
- `destino` só aceito se começar com `/` e não com `//`; caso contrário, usa `/`.
- `ConcluirLoginOAuth`: confere `state` com o cookie e o estado salvo (uso único); troca o código; resolve o usuário nesta ordem:
  1. identidade `(provedor, subject)` existente;
  2. recusa se `email_verificado` for falso;
  3. usuário existente com o mesmo e-mail: cria a identidade, marca o e-mail como verificado e **apaga credencial de senha**;
  4. caso contrário, cria `Perfil` (`u-` + 12 hex), `Usuario` e identidade.
- Provedores resolvidos por dicionário `{nome: ProvedorIdentidade}`; provedor desconhecido gera erro de domínio.
- Cria a sessão ao final (reaproveitando o serviço da tarefa 4.0).
</requirements>

## Subtarefas

- [ ] 5.1 `IniciarLoginOAuth` (testes primeiro).
- [ ] 5.2 `ConcluirLoginOAuth` com os quatro caminhos de resolução.
- [ ] 5.3 Testes de segurança: `state` inválido, reaproveitado ou expirado; provedor desconhecido; e-mail não verificado.

## Detalhes de Implementação

Ver "Fluxo de dados" e "Resolução da identidade" em `techspec-job-0013.md`. Usar o `ProvedorIdentidade` fake nos testes.

## Critérios de Sucesso

- Perfil legado pré-criado pelo mantenedor é vinculado no primeiro login com e-mail verificado.
- Credencial de senha anterior à verificação não sobrevive ao vínculo.
- O mesmo `state` não funciona duas vezes.

## Testes da Tarefa

- [ ] Testes de unidade com fakes

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/autenticacao/service_layer/iniciar_login_oauth/service.py`
- `src/jobsync/autenticacao/service_layer/concluir_login_oauth/service.py`
- `src/jobsync/tests/autenticacao/`

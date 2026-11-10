# Tarefa 3.0: Adapters externos (`HasherSenhaArgon2`, `EnviadorEmail*`, `ProvedorGoogle`)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar os adapters das portas externas definidas na tarefa 2.0. Complexidade: high.

<requirements>
- `HasherSenhaArgon2`: Argon2id com parâmetros-padrão de `argon2-cffi`; `conferir` devolve `False` para hash inválido, sem lançar exceção.
- `EnviadorEmailSmtp` (`smtplib`, configurado por `SMTP_HOST/PORT/USER/PASSWORD/FROM`) e `EnviadorEmailLog` (registra o link em log, para desenvolvimento).
- `ProvedorGoogle`: monta a URL de autorização com PKCE (`code_challenge` S256), `state` e `nonce`; troca o `code` por tokens via `httpx`; valida o ID token (assinatura via JWKS, `iss`, `aud`, `exp`, `nonce`) e devolve `IdentidadeAutenticada`.
- Falhas de rede ou resposta inválida viram uma exceção de domínio única (`ProvedorIndisponivel`), sem expor detalhes.
- Adicionar `argon2-cffi` e `PyJWT[crypto]` a `requirements-backend.txt` e `requirements.txt`, com versões fixas.
- Segredos só por variável de ambiente; nada de senha, token ou `code` em log.
</requirements>

## Subtarefas

- [x] 3.1 Escrever testes e implementar `HasherSenhaArgon2`.
- [x] 3.2 Escrever testes e implementar `EnviadorEmailSmtp` e `EnviadorEmailLog`.
- [x] 3.3 Escrever testes com `httpx.MockTransport` e implementar `ProvedorGoogle`.
- [x] 3.4 Atualizar os arquivos de requisitos.

## Detalhes de Implementação

Ver "Pontos de Integração" e "Decisões Principais" em `techspec-job-0013.md`. Documentação do Google: https://developers.google.com/identity/openid-connect/openid-connect. PKCE: RFC 7636.

## Critérios de Sucesso

- ID token com `aud`, `iss`, `exp`, `nonce` ou assinatura inválidos é recusado.
- `email_verified = false` chega ao serviço como `email_verificado = False`, sem erro.
- Nenhum teste faz chamada de rede real.

## Testes da Tarefa

- [x] Testes de unidade dos três adapters (rede e SMTP simulados)

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/autenticacao/adapters/hasher_senha_argon2.py`
- `src/jobsync/autenticacao/adapters/enviador_email_smtp.py`
- `src/jobsync/autenticacao/adapters/enviador_email_log.py`
- `src/jobsync/autenticacao/adapters/provedor_google.py`
- `requirements.txt`, `requirements-backend.txt`
- `src/jobsync/tests/autenticacao/`

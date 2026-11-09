# Resumo de Tarefas de Implementação do Botão Confirmar Candidatura (JOB-0037)

## Tarefas

- [x] 1.0 Regra do limite de currículos no domínio `curriculo_salvo` e refatoração do `SalvarCurriculo`
- [x] 2.0 Fábrica `Candidatura.nova` e ajuste do `CriarCandidatura`
- [x] 3.0 Caso de uso `ConfirmarCandidaturaAjustada`
- [x] 4.0 Endpoint `POST /v1/candidaturas-ajustadas`, handler 409 e coleção Postman
- [x] 5.0 Cliente de API e tipos do frontend
- [ ] 6.0 Botão "Confirmar candidatura" e estados na tela de ajuste
- [ ] 7.0 E2E, acessibilidade, suíte completa e `lint-imports`

## Dependências

- 1.0 e 2.0 não dependem de nenhuma outra tarefa e podem ser feitas em paralelo.
- 1.0 e 2.0 devem ser concluídas antes de 3.0.
- 3.0 deve ser concluída antes de 4.0.
- 4.0 deve ser concluída antes de 5.0 (o cliente usa o contrato OpenAPI do endpoint).
- 5.0 deve ser concluída antes de 6.0.
- 1.0 a 6.0 devem ser concluídas antes de 7.0.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Regra do limite no domínio | low | — | `garantir_espaco` no limite e abaixo dele; `SalvarCurriculo` com o mesmo comportamento e as mesmas exceções |
| 2.0 | Fábrica `Candidatura.nova` | low | — | Status `APLICADO` e histórico inicial; `CriarCandidatura` continua passando |
| 3.0 | Caso de uso de confirmação | high | 1.0, 2.0 | Cria currículo, vaga e candidatura; biblioteca cheia não grava nada; compensação remove o currículo; vaga convertida fora de "Vagas salvas" |
| 4.0 | Endpoint, handler 409 e Postman | medium | 3.0 | Router: 201, 409, 422 (PDF inválido, base64 inválido, empresa vazia); SQLite temporário aceita as chaves estrangeiras |
| 5.0 | Cliente de API e tipos | low | 4.0 | `HttpApiClient` envia o corpo certo e converte 409 e 422 em `ApiError`; `schema.d.ts` sem diferença no CI |
| 6.0 | Botão e estados | medium | 5.0 | Botão só com PDF; desabilitado sem empresa; sucesso com link; 409 e erro genérico; novo PDF reinicia; listas invalidadas |
| 7.0 | Entrega | medium | 1.0 a 6.0 | E2E do fluxo completo; axe sem violações graves; `pytest`, Vitest e `lint-imports` verdes |

## Entregáveis principais

- Botão "Confirmar candidatura" na tela "Ajustar para uma vaga", visível só com PDF gerado.
- Candidatura criada em Aplicado, com empresa, cargo e o PDF exato que o candidato gerou, ligado a um currículo salvo.
- Vaga guardada já como convertida, fora de "Vagas salvas".
- Nenhum registro pela metade: biblioteca cheia não grava nada, e falhas intermediárias desfazem o currículo salvo.
- Regra do limite de 10 currículos em um único lugar do sistema.
- Nenhum endpoint existente muda.

# Tarefa 2.0: Cliente HTTP seguro com proteção contra SSRF

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar `ClienteHttpSeguro` em `shared_kernel/adapters`, usado por todos os leitores de página. Ele impede que o servidor acesse endereços internos a partir de URLs informadas por usuários.

Complexidade: high. Dependências: nenhuma.

<requirements>
- Aceitar apenas `http` e `https`.
- Resolver o DNS e recusar IPs de loopback, redes privadas, link-local e metadados de nuvem, para a URL inicial e para cada redirecionamento.
- Limitar redirecionamentos (5), tamanho da resposta (2 MB) e tempo (15 s, configurável).
- Conectar no IP validado, mantendo o nome original no SNI e no cabeçalho `Host`. Validar o suporte do `httpx`; se não for possível, revalidar o IP imediatamente antes de conectar e documentar a janela residual na techspec.
- Não repetir a requisição após resposta 429.
- Devolver status, corpo (texto) e URL final, ou levantar uma exceção própria com o motivo (`endereco_recusado`, `excesso_redirecionamentos`, `tamanho_excedido`, `tempo_esgotado`, `falha_de_rede`).
</requirements>

## Subtarefas

- [ ] 2.1 Escrever os testes (IPs privados, loopback, metadados, redirecionamento para IP interno, limites, esquemas inválidos).
- [ ] 2.2 Implementar a validação de endereço com resolvedor injetável.
- [ ] 2.3 Implementar o cliente com limites e redirecionamento manual.
- [ ] 2.4 Verificar e registrar o resultado do teste de SNI com IP fixo.

## Detalhes de Implementação

Ver "Pontos de Integração" e "Riscos Conhecidos" da techspec. Usar `httpx` (já no projeto). Os testes usam `httpx.MockTransport` e um resolvedor falso.

## Critérios de Sucesso

- Nenhuma requisição é feita para endereços recusados (critério 7 do PRD).
- Os limites são respeitados nos testes.

## Testes da Tarefa

- [ ] Testes de unidade: `TestClienteHttpSeguro`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/prd-job-0047.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/techspec-job-0047.md`
- `src/jobsync/shared_kernel/adapters/`
- `src/jobsync/vaga_externa/adapters/extrator_texto_pagina_client.py`
- `src/jobsync/tests/shared_kernel/`

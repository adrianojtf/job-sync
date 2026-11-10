# Tarefa 7.0: Proteger os routers existentes por sessão e perfil

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Hoje os routers confiam no `perfil_identificador` enviado pelo cliente. Esta tarefa exige sessão em todas as rotas de dados e confere se o perfil pedido é o da sessão, sem mudar parâmetros nem corpos. Complexidade: high.

<requirements>
- `exigir_acesso_ao_perfil(perfil_identificador, usuario)` lança `AcessoNegado` (403) quando o perfil não é o do usuário autenticado.
- Aplicar em todos os routers com `perfil_identificador` (query, path ou corpo): candidatura, curriculo, perfil, perfil_estruturado, token_captura, vaga.
- Rotas sem `perfil_identificador` que expõem dados do usuário também exigem sessão.
- `GET /perfis/{id}` deixa de criar perfil: devolve o perfil da sessão ou 403.
- `vaga_externa_router` (captura por token), `health` e os routers da tarefa 6.0 ficam públicos.
- Teste que percorre `app.routes` e exige 401 sem sessão em toda rota fora da lista explícita de rotas públicas.
- Testes existentes dos routers passam a autenticar via dublê de sessão.
</requirements>

## Subtarefas

- [x] 7.1 Implementar `exigir_acesso_ao_perfil` com testes.
- [x] 7.2 Aplicar em `perfil_router` e `perfil_estruturado_router`.
- [x] 7.3 Aplicar em `curriculo_router` e `candidatura_router`.
- [x] 7.4 Aplicar em `vaga_router` e `token_captura_router`.
- [x] 7.5 Teste de varredura de rotas e ajuste dos testes existentes.

## Detalhes de Implementação

Ver "Componentes existentes alterados", "Riscos Conhecidos" e "Conformidade com Padrões" em `techspec-job-0013.md`. Usar `grep -rn perfil_identificador src/jobsync/entrypoints/api/routers` para o inventário.

## Achados durante a execução

- `POST /candidaturas/{id}/submissao` não trazia perfil na entrada e não conferia o dono: qualquer usuário autenticado podia mover candidaturas alheias pelo `id`. Passou a responder 404 para candidatura de outro perfil.
- A extensão Chrome usa o servidor separado `servidor_captura.py` (token Bearer), então `POST /v1/vagas` ficou só para o frontend e exige sessão.
- A proteção é uma dependência de router (`exigir_perfil_da_requisicao`): rota nova nasce protegida. Um teste varre `app.routes` e confere 401 sem sessão e 403 com perfil alheio no caminho, na query ou no corpo.

## Critérios de Sucesso

- Sem sessão, toda rota de dados responde 401.
- Com sessão de outro usuário, toda rota com `perfil_identificador` responde 403.
- Suíte completa de testes de API passa.

## Testes da Tarefa

- [x] Testes de API por router (401, 403 e caminho feliz)
- [x] Teste de varredura de rotas

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/routers/*.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/tests/entrypoints/api/`

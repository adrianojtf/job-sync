# Tarefa 6.0: Endpoint `POST /v1/vagas/extracoes`, handlers de erro, injeção e configuração

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expor o caso de uso na API, com schemas, handlers RFC 7807, injeção de dependências e variáveis de ambiente.

Complexidade: medium. Dependências: 5.0.

<requirements>
- `POST /v1/vagas/extracoes` com corpo `{url?, texto?}` (pelo menos um) e resposta 200 com `DadosVagaResponse`.
- Erros: 422 (link inválido, sem dados, fonte não suportada), 429 com `Retry-After` e 502 (leitura indisponível), todos em RFC 7807 por handlers centrais.
- Rota sob `exigir_perfil_da_requisicao`. O limite usa o usuário autenticado.
- Variáveis: `VAGA_LEITURA_LINKEDIN_HABILITADA` (true), `VAGA_LEITURA_LIMITE_POR_MINUTO` (10), `VAGA_LEITURA_LIMITE_POR_DIA` (100), `VAGA_LEITURA_TIMEOUT_SEGUNDOS` (15).
- O limitador é uma instância única por processo.
- Logs conforme "Monitoramento e Observabilidade" da techspec, sem conteúdo da vaga nem URL completa.
</requirements>

## Subtarefas

- [ ] 6.1 Escrever os testes do roteador (200, 422, 429, 502, 401).
- [ ] 6.2 Criar os schemas `ExtracaoVagaRequest` e `DadosVagaResponse`.
- [ ] 6.3 Adicionar a rota em `vaga_router.py`.
- [ ] 6.4 Registrar os handlers em `exceptions.py`.
- [ ] 6.5 Compor o serviço, os leitores e o limitador em `dependencies.py`.
- [ ] 6.6 Adicionar as variáveis em `.env.example`.

## Detalhes de Implementação

Ver "Endpoints de API" da techspec. Seguir os padrões de `/vagas/avaliacoes` e de `AvaliacaoDescricaoVagaIndisponivel`.

## Critérios de Sucesso

- Todos os códigos de status da techspec são cobertos por testes.
- O OpenAPI expõe a nova rota.

## Testes da Tarefa

- [ ] Testes de API em `tests/entrypoints/api/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/prd-job-0047.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/techspec-job-0047.md`
- `src/jobsync/entrypoints/api/routers/vaga_router.py`
- `src/jobsync/entrypoints/api/schemas/vaga.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/entrypoints/api/exceptions.py`
- `.env.example`

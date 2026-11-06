# Tarefa 3.0: Disponibilizar avaliação de descrição de vaga pela API

<critical>Ler `prd-job-0013.md` e `techspec-job-0013.md` desta pasta antes de iniciar a tarefa.</critical>

## Visão Geral

Entregar a avaliação sob demanda de uma descrição de vaga, usando Jev para gerar score e categorias nas dimensões definidas pelo produto.

<requirements>
- Criar o caso de uso e a porta de avaliação no domínio de vaga.
- Avaliar completude, clareza, relevância e inclusão por dimensões estruturadas.
- Expor `POST /v1/vagas/avaliacoes` com schemas Pydantic de entrada e resposta.
- Retornar score geral de 0 a 100 e score/categoria por dimensão, sem texto livre gerado pelo modelo.
- Não persistir descrição nem resultado da avaliação.
- Documentar sucesso e erros do provedor no OpenAPI.
</requirements>

## Subtarefas

- [x] 3.1 Criar `AvaliadorDescricaoVagaPort`, modelo de resultado e serviço `AvaliarDescricaoVaga`.
- [x] 3.2 Implementar o adapter Jev para as dimensões de vaga e mapear a resposta para o domínio.
- [x] 3.3 Criar request/response schemas e registrar `POST /v1/vagas/avaliacoes`.
- [x] 3.4 Injetar o caso de uso na composição FastAPI e documentar status codes e exemplos.

## Detalhes de Implementação

Usar os contratos e a normalização da tarefa 2.0. Manter `JobDescriptionAnalyzerClient` como análise de requisitos para os fluxos existentes; este endpoint é uma avaliação de qualidade separada.

## Critérios de Sucesso

- O endpoint valida entrada, retorna dimensões e score na escala esperada e não persiste dados.
- Os quatro critérios são avaliados com rubricas fixas; score desfavorável não dispara bloqueio de adaptação.
- Falhas de autenticação, timeout ou resposta inválida do Jev chegam ao handler central sem expor dados internos.

## Testes da Tarefa

- [x] Testes unitários do serviço e adapter com respostas fakes para cada dimensão.
- [x] Testes da API para sucesso, validação de entrada e falha do provedor.
- [x] Verificar `response_model`, exemplos e status codes no OpenAPI.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/vaga/domain/`
- Novo `src/jobsync/vaga/service_layer/avaliar_descricao_vaga/`
- `src/jobsync/vaga/adapters/`
- `src/jobsync/entrypoints/api/routers/vaga_router.py`
- `src/jobsync/entrypoints/api/schemas/vaga.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/tests/vaga/` e testes da API

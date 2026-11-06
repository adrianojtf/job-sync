# Tarefa 4.0: Disponibilizar avaliação de experiência pela API

<critical>Ler `prd-job-0013.md` e `techspec-job-0013.md` desta pasta antes de iniciar a tarefa.</critical>

## Visão Geral

Entregar a avaliação sob demanda de uma experiência profissional em relação a uma descrição de vaga, sem alterar ou salvar o texto avaliado.

<requirements>
- Criar o caso de uso e a porta de avaliação no domínio de currículo.
- Avaliar clareza/escrita, qualidade/detalhe, aderência à vaga e consistência textual.
- Expor `POST /v1/experiencias-profissionais/avaliacoes` com schemas Pydantic de entrada e resposta.
- Retornar score geral de 0 a 100 e score/categoria por dimensão, sem explicações livres.
- Receber a descrição da vaga como contexto e não verificar fatos em fontes externas.
- Não persistir nem modificar a experiência avaliada.
</requirements>

## Subtarefas

- [x] 4.1 Criar `AvaliadorExperienciaPort`, modelo de resultado e serviço `AvaliarExperiencia`.
- [x] 4.2 Implementar o adapter Jev para as dimensões e critérios de consistência textual.
- [x] 4.3 Criar request/response schemas e registrar `POST /v1/experiencias-profissionais/avaliacoes`.
- [x] 4.4 Injetar o caso de uso na composição FastAPI e documentar status codes e exemplos.

## Detalhes de Implementação

Usar `ExperienciaParaAvaliacao` e os contratos Jev definidos na tarefa 2.0. A requisição contém o texto individual da experiência e a vaga-alvo; ela não exige que a experiência seja previamente persistida em um perfil.

## Critérios de Sucesso

- O endpoint retorna as quatro dimensões e um score agregado entre 0 e 100.
- O resultado não afirma que informações foram verificadas fora do texto fornecido.
- A avaliação não modifica nem persiste a experiência ou a descrição da vaga.

## Testes da Tarefa

- [x] Testes unitários do serviço e adapter com fakes, cobrindo cada dimensão e consistência textual.
- [x] Testes da API para sucesso, dados inválidos e indisponibilidade do provedor.
- [x] Verificar schemas, exemplos, `response_model` e erros documentados no OpenAPI.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/`
- Novo `src/jobsync/curriculo/service_layer/avaliar_experiencia/`
- `src/jobsync/curriculo/adapters/`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/entrypoints/api/schemas/curriculo.py`
- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/tests/curriculo/` e testes da API

# Tarefa 6.0: Casos de uso e endpoints de `/curriculos-adaptados`

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cria os casos de uso de salvar, atualizar, buscar e listar currículos adaptados e os endpoints que os expõem. Salvar e atualizar regeneram o PDF.

<requirements>
- Um caso de uso por pasta em `curriculo_adaptado/service_layer/` (`service.py`, `dtos.py`, `validator.py`), no padrão de `curriculo_salvo`.
- `POST /curriculos-adaptados`: salva o rascunho revisado com os dados da vaga e devolve `id` e o PDF no formato de `CurriculoRevisadoResponse`.
- `GET /curriculos-adaptados`: lista resumida (id, nome, cargo, empresa, atualizado em).
- `GET /curriculos-adaptados/{id}`: conteúdo completo e contexto da vaga.
- `PUT /curriculos-adaptados/{id}`: substitui o rascunho, regenera o PDF e devolve o PDF (a atualização do PDF vinculado é a tarefa 7.0).
- Rotas sob `exigir_perfil_da_requisicao`; 404 para id de outro perfil; 422 para conteúdo inválido.
- Injeção de dependências dos serviços novos.
- `POST /curriculos-revisados` permanece.
</requirements>

## Subtarefas

- [ ] 6.1 Testes dos serviços com repositório fake e gerador de PDF falso (red): salvar, atualizar, buscar, listar, isolamento por perfil, 404, validação.
- [ ] 6.2 Testes de routers e schemas (red).
- [ ] 6.3 Implementar os quatro casos de uso (green).
- [ ] 6.4 Criar `curriculo_adaptado_router.py`, schemas e registro na aplicação (green).
- [ ] 6.5 Atualizar a collection Postman com os novos endpoints.
- [ ] 6.6 Logs `info` ao salvar e atualizar, sem o conteúdo do currículo.

## Detalhes de Implementação

Techspec: "Endpoints de API", "Pontos de Integração" e "Monitoramento e Observabilidade". PRD: RF 8, 10 e 12.

## Critérios de Sucesso

- Criar, listar, abrir e editar um currículo adaptado funciona pela API, com o PDF refletindo o conteúdo editado.
- Um perfil não acessa currículos de outro.

## Testes da Tarefa

- [ ] Testes de unidade dos serviços.
- [ ] Testes de routers e schemas.
- [ ] Regressão: `src/jobsync/tests/entrypoints/api/` e `src/jobsync/tests/curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo_adaptado/service_layer/` (novo)
- `src/jobsync/entrypoints/api/routers/curriculo_adaptado_router.py` (novo)
- `src/jobsync/entrypoints/api/schemas/`
- `src/jobsync/curriculo/domain/gerador_pdf_port.py`
- `job-sync.postman_collection.json`

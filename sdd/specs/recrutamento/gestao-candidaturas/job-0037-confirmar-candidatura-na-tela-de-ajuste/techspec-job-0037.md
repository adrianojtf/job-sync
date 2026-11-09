# Especificação Técnica — JOB-0037

PRD de referência: `prd-job-0037.md` (mesmo diretório).

## Resumo Executivo

A confirmação vira um caso de uso novo, `ConfirmarCandidaturaAjustada`, no domínio `candidatura`. Ele recebe os dados da vaga e o PDF gerado e cria, nesta ordem: o currículo salvo, a vaga e a candidatura `APLICADO`. A vaga é marcada como convertida no fim. O caso de uso usa só portas de repositório (de `candidatura`, `vaga` e `curriculo_salvo`) e não chama outro caso de uso, como pedem as regras de camadas do projeto.

O backend ganha um endpoint novo, `POST /v1/candidaturas-ajustadas`, que recebe o PDF em base64 e devolve a candidatura criada. O frontend ganha o botão no cartão do PDF, uma mutation nova e a invalidação das listas afetadas.

A regra do limite de 10 currículos por perfil sobe para o domínio `curriculo_salvo`, para ser usada pelo caso de uso existente e pelo novo, sem duplicação.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Backend (`src/jobsync`):

| Componente | Situação | Responsabilidade |
|---|---|---|
| `candidatura/service_layer/confirmar_candidatura_ajustada/` (`service.py`, `dtos.py`, `validator.py`, `__init__.py`) | **Novo** | Caso de uso `ConfirmarCandidaturaAjustada` |
| `curriculo_salvo/domain/limite_curriculos_salvos.py` | **Novo** | `LIMITE_CURRICULOS_POR_PERFIL`, `LimiteCurriculosSalvosExcedido` e `garantir_espaco(quantidade_atual)` |
| `curriculo_salvo/service_layer/salvar_curriculo/service.py` e `__init__.py` | **Modificado** | Usa a regra do domínio e continua exportando os mesmos nomes (o Streamlit importa daqui) |
| `candidatura/service_layer/confirmar_candidatura_ajustada/__init__.py` | **Novo** | Exporta o caso de uso, o DTO e o validador (o `candidatura/__init__.py` exporta só o domínio, como já acontece com `CriarCandidatura`) |
| `entrypoints/api/schemas/candidatura.py` | **Modificado** | `CandidaturaConfirmarRequest` |
| `entrypoints/api/routers/candidatura_router.py` | **Modificado** | Endpoint novo |
| `entrypoints/api/dependencies.py` | **Modificado** | `ServiceConfirmarCandidaturaAjustadaDep` com os 3 repositórios |
| `entrypoints/api/exceptions.py` | **Modificado** | Handler de `LimiteCurriculosSalvosExcedido` com 409 |
| `job-sync.postman_collection.json` | **Modificado** | Requisição nova |

Frontend (`frontend/src`):

| Componente | Situação | Responsabilidade |
|---|---|---|
| `api/api-client.ts`, `http-api-client.ts`, `tipos.ts`, `schema.d.ts` | **Modificado** | `confirmarCandidaturaAjustada` e tipos (schema regenerado com Python 3.12, o mesmo do CI) |
| `features/ajustar-vaga/use-ajustar-vaga.ts` | **Modificado** | Mutation `confirmarCandidatura`; invalida candidaturas, currículos e vagas |
| `features/ajustar-vaga/AjustarVagaPage.tsx` | **Modificado** | Guarda a vaga do PDF gerado; botão e estados no `CurriculoGerado` |
| `features/ajustar-vaga/AjustarVagaPage.test.tsx`, `frontend/e2e/*` | **Modificado** | Testes |

Fluxo de dados:

1. O usuário gera o PDF. A tela guarda uma cópia da vaga usada (`cargo_alvo`, `empresa_alvo`, `descricao_vaga`) junto do PDF.
2. O clique envia `POST /v1/candidaturas-ajustadas`.
3. O caso de uso valida, confere o limite, grava currículo, vaga e candidatura, e marca a vaga como convertida.
4. A tela mostra o sucesso e invalida as listas.

## Design de Implementação

### Interfaces Principais

```python
@dataclass(frozen=True)
class ConfirmarCandidaturaAjustadaInputDto:
    perfil_identificador: str
    cargo: str
    empresa: str
    descricao_vaga: str
    nome_arquivo: str
    pdf_bytes: bytes

@dataclass
class ConfirmarCandidaturaAjustada:
    repositorio_candidatura: CandidaturaRepository
    repositorio_vaga: VagaRepository
    repositorio_curriculo_salvo: CurriculoSalvoRepository

    def executar(self, input_dto: ConfirmarCandidaturaAjustadaInputDto) -> Candidatura: ...
```

```python
# curriculo_salvo/domain/limite_curriculos_salvos.py
def garantir_espaco(quantidade_atual: int) -> None:
    """Levanta LimiteCurriculosSalvosExcedido quando a biblioteca já tem o limite."""
```

Ordem de `executar`, exigida pelas chaves estrangeiras da tabela `candidatura` (`vaga_id` e `curriculo_salvo_id`):

1. Validar o DTO: perfil, cargo, empresa, descrição e nome do arquivo preenchidos; PDF começando com `%PDF`.
2. `contar_por_perfil` e `garantir_espaco`. Sem espaço, nada foi gravado.
3. Salvar o `CurriculoSalvo` (`nome_referencia` = nome do arquivo gerado).
4. Salvar a `Vaga` com a descrição.
5. `marcar_como_convertida(vaga_id)`.
6. Salvar a `Candidatura` com `Candidatura.nova` (status `APLICADO` e histórico inicial).

A vaga é marcada como convertida **antes** da candidatura (ajuste feito na implementação, em relação ao desenho inicial). Assim, se a candidatura falhar, a vaga já está convertida e não aparece em "Vagas salvas", o que atende o RF 7 do PRD.

Compensação: se o passo 4, 5 ou 6 falhar, o caso de uso remove o currículo salvo (`remover`), registra um `WARNING` com os identificadores e o tipo do erro (sem dados pessoais) e relança o erro original. Se a própria remoção falhar, registra outro `WARNING` e o erro original continua sendo o relançado. Não há `remover` de vaga na porta, e criar um não faz parte deste JOB: uma vaga já convertida pode sobrar, sem aparecer ao usuário.

Reaproveitamento: a montagem da `Candidatura` repete a de `CriarCandidatura`. Para não duplicar (DRY), extrair uma fábrica `Candidatura.nova(...)` no domínio, usada pelos dois casos de uso.

### Modelos de Dados

Sem tabela ou coluna nova e sem status novo. Usa `curriculo_salvo`, `vaga` e `candidatura` como estão.

### Endpoints de API

| Método e caminho | Situação | Descrição |
|---|---|---|
| `POST /v1/candidaturas-ajustadas` | **Novo** | Cria vaga, currículo salvo e candidatura `APLICADO` a partir do PDF gerado |

Requisição (`CandidaturaConfirmarRequest`):

```json
{"perfil_identificador": "ana", "cargo": "Engenheiro de Software", "empresa": "TechCorp",
 "descricao_vaga": "Texto da vaga...", "nome_arquivo": "AnaSouza-2026-11-09-Engenheiro-TechCorp.pdf",
 "pdf_base64": "JVBERi0x..."}
```

Respostas:

- **201** com `CandidaturaResponse` (o mesmo schema de `POST /v1/candidaturas`).
- **409** `ProblemaResponse` quando a biblioteca está cheia, via handler central.
- **422** quando um campo está vazio ou o PDF é inválido, como nos outros endpoints.

O caminho segue o padrão dos recursos compostos já existentes (`/curriculos-revisados`, `/experiencias-adaptadas`). Os endpoints atuais não mudam.

Observação: `POST /v1/curriculos` devolve 422 para a mesma condição de biblioteca cheia, porque captura `ValueError` no próprio router. Esse comportamento não é tocado aqui, e o 409 vale só para o endpoint novo.

### Frontend

- `confirmarCandidaturaAjustada(dados)` no `ApiClient`, com `pdf_base64` e `nome_arquivo` vindos do PDF gerado.
- O `CurriculoGerado` recebe a vaga do PDF e o estado da mutation. Estados: inicial, enviando, confirmado e erro.
- Empresa em branco: botão desabilitado com a explicação do PRD.
- Novo PDF gerado: `confirmarCandidatura.reset()` volta o botão ao estado inicial (RF 12).
- Em sucesso, invalidar `chaveCandidaturas`, `chaveCurriculos` e `chaveVagas` do perfil.
- A mensagem de sucesso e a de erro usam `role="status"` e `role="alert"`, como as outras telas.

## Pontos de Integração

Nenhum serviço externo. O PDF vai do navegador para a API em base64, como já acontece em `POST /v1/curriculos-revisados`, só que no sentido inverso.

## Abordagem de Testes

TDD, conforme `.windsurf/rules/testing-rules.md`: AAA, `Test<Classe>`, sem comentários, mocks só para portas.

### Testes Unidade

Backend:

- `ConfirmarCandidaturaAjustada` (com repositórios fake): cria currículo, vaga e candidatura `APLICADO` com empresa, cargo e `curriculo_salvo_id` corretos; marca a vaga como convertida; a vaga não aparece em `listar_nao_convertidas`.
- Biblioteca com 10 currículos: levanta `LimiteCurriculosSalvosExcedido` e não grava nada (verificar os três repositórios).
- Falha ao salvar a vaga, ao marcá-la como convertida ou ao salvar a candidatura remove o currículo salvo; na falha da candidatura, a vaga fica convertida e fora de "Vagas salvas".
- Falha ao remover o currículo na compensação não esconde o erro original e registra `WARNING`.
- Validação: campos vazios e PDF sem `%PDF`.
- `garantir_espaco` no limite e abaixo dele; `SalvarCurriculo` continua com o mesmo comportamento e as mesmas exceções.
- Fábrica `Candidatura.nova`: status e histórico iniciais; `CriarCandidatura` segue passando.
- Router: 201 com o corpo da candidatura, 409 com biblioteca cheia, 422 com PDF inválido, base64 inválido e empresa vazia.
- Com os repositórios SQLite em um banco temporário: a candidatura criada aparece em `listar_por_perfil` com status `APLICADO`, e as chaves estrangeiras de vaga e currículo são aceitas.

Frontend (Vitest):

- O botão só aparece com PDF gerado e fica desabilitado sem empresa.
- Clique envia o corpo esperado (`cargo`, `empresa`, `descricao_vaga`, `nome_arquivo`, `pdf_base64`, perfil).
- Sucesso mostra a mensagem e o link para o board, e desabilita o botão.
- 409 mostra a mensagem de biblioteca cheia; outro erro permite tentar de novo.
- Gerar novo PDF volta o botão ao estado inicial.
- As listas de candidaturas, currículos e vagas são invalidadas.

### Testes de Serviço

- E2E (Playwright): ajustar, gerar o PDF, confirmar e ver a candidatura em Aplicado no board, com o PDF baixável no detalhe. Os dublês de IA do `app_e2e.py` seguem determinísticos.
- Acessibilidade (axe) com o botão e as mensagens novas.
- `lint-imports`: confirmar que `candidatura` importar de `vaga` e de `curriculo_salvo` não cria ciclo entre domínios.
- Contrato: regenerar `schema.d.ts` com Python 3.12.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Regra do limite no domínio `curriculo_salvo` e refatoração de `SalvarCurriculo`.
2. Fábrica `Candidatura.nova` e ajuste de `CriarCandidatura`.
3. Caso de uso `ConfirmarCandidaturaAjustada` com testes.
4. Schema, endpoint, injeção, handler 409 e Postman.
5. Cliente de API e tipos do frontend (schema com Python 3.12).
6. Mutation, botão e estados na tela.
7. E2E, acessibilidade e suíte completa.

### Dependências Técnicas

Nenhuma bloqueante. As tarefas 1 e 2 não dependem uma da outra.

## Monitoramento e Observabilidade

- `INFO` ao confirmar: identificadores gerados e tamanho do PDF em bytes, sem conteúdo.
- `WARNING` quando `marcar_como_convertida` falhar ou a compensação rodar.
- Nunca registrar o PDF, a descrição da vaga, o nome do candidato nem a empresa.

## Considerações Técnicas

### Decisões Principais

| Decisão | Justificativa | Alternativa rejeitada |
|---|---|---|
| Um caso de uso e um endpoint no backend | A regra de limite e a ordem das chaves ficam no servidor, e o resultado é consistente | O frontend encadear 3 chamadas existentes: deixaria registros pela metade se uma falhasse |
| Enviar o PDF gerado em base64 | Garante que a candidatura guarda o arquivo que o usuário viu | Reconstruir o PDF no servidor a partir do rascunho: mais leve, mas pode diferir do que foi baixado |
| Regra do limite no domínio `curriculo_salvo` | Um único lugar para a regra (DRY) | Copiar a constante e a verificação no caso de uso novo |
| 409 só no endpoint novo | Status mais específico, sem mexer no contrato atual | Mudar `POST /v1/curriculos` para 409 (quebra de contrato) |
| Candidatura em `APLICADO` | Decisão de produto: sem status novo | Novo status "Em andamento" (muda enum, board e contrato) |

### Riscos Conhecidos

- **Sem transação única:** cada repositório SQLite grava por conta própria. A compensação cobre currículo e vaga, mas uma falha no passo 5 (marcar a vaga como convertida) deixa a vaga pendente em "Vagas salvas", e uma falha no passo 6 deixa uma vaga convertida sem candidatura, invisível ao usuário. Verificar na implementação se uma conexão compartilhada permite uma transação só.
- **Biblioteca poluída:** os PDFs confirmados entram na lista de currículos-base (questões 1 e 2 do PRD).
- **Duplicidade:** dois cliques rápidos podem criar duas candidaturas. O botão desabilita ao enviar, mas o servidor não é idempotente.
- **Tamanho do corpo:** o PDF em base64 cresce cerca de um terço. Verificar o limite de corpo do servidor e do Nginx para um PDF de 2 páginas (o gerado hoje tem cerca de 55 KB).
- **Empresa opcional na tela de ajuste:** sem empresa, a confirmação fica bloqueada. Se isso incomodar, a questão 4 do PRD resolve.

### Conformidade com Padrões

- `code-design-standards.md`: caso de uso em `service_layer` do domínio dono do resultado, com repositórios de outros domínios injetados como porta; agregados ligados por identificador; regra de limite no `domain`, sem infraestrutura.
- `back-end-general-rules.md`: recurso composto no plural e com hífen, `POST` com 201, 409 e 422, erro no formato Problem Details pelo handler central, contrato existente intocado.
- `testing-rules.md`: `Test<Classe>`, AAA, sem comentários.
- `AGENTS.md`: DRY (limite e fábrica de candidatura), SOLID (um caso de uso por ação), Tell Don't Ask (`garantir_espaco`), hexagonal e TDD.
- Desvio: nenhum identificado.

### Arquivos relevantes e dependentes

- `src/jobsync/candidatura/domain/candidatura.py`, `candidatura_repository.py`
- `src/jobsync/candidatura/service_layer/criar_candidatura/service.py`
- `src/jobsync/curriculo_salvo/domain/curriculo_salvo.py`, `curriculo_salvo_repository.py`
- `src/jobsync/curriculo_salvo/service_layer/salvar_curriculo/`
- `src/jobsync/vaga/domain/vaga.py`, `vaga_repository.py`
- `src/jobsync/entrypoints/api/{routers/candidatura_router.py,schemas/candidatura.py,dependencies.py,exceptions.py}`
- `src/jobsync/entrypoints/streamlit_app.py` (importa `LimiteCurriculosSalvosExcedido`)
- `src/jobsync/shared_kernel/adapters/persistence/_conexao_sqlite.py` (chaves estrangeiras)
- `frontend/src/features/ajustar-vaga/{AjustarVagaPage.tsx,use-ajustar-vaga.ts}`
- `frontend/src/features/candidaturas/DetalheCandidaturaModal.tsx` (já baixa o PDF do currículo salvo)
- `frontend/src/api/*`, `frontend/e2e/*`, `job-sync.postman_collection.json`

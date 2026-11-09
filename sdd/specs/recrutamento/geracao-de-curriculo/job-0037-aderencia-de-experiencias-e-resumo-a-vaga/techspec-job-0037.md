# Especificação Técnica — JOB-0037

PRD de referência: `prd-job-0037.md` (mesmo diretório).
Parte de: JOB-0034 e JOB-0035, já integradas na `main`.

## Resumo Executivo

A solução tem três partes.

1. **Contexto completo da vaga.** `ContextoVaga` passa a carregar o `cargo_alvo`. As portas de ajuste (`AjustadorExperienciaPort`, `AjustadorTextoPort`) passam a receber um `ContextoVaga` no lugar de três parâmetros soltos. Hoje o `cargo_alvo` chega ao `AdaptarCurriculoParaVagaInputDto`, mas nenhum adapter de IA o recebe.
2. **Plano de adaptação.** Antes de ajustar as experiências, uma nova porta (`IdentificadorEquivalenciasPort`) faz uma única chamada de IA e devolve pares de tecnologias equivalentes (original → pedida pela vaga). Um objeto de domínio determinístico (`PlanoAdaptacao`) distribui as trocas entre as experiências, com a regra do PRD (ao menos uma experiência mantém a original). Cada chamada de `ajustar` recebe as diretrizes da sua experiência.
3. **Refino variável.** Um VO `PedidoRefino` (tentativa e sugestões anteriores) escolhe um `FocoRefino` em rodízio. As portas de sugestão passam a recebê-lo. O `AjustadorTextoPort` ganha `refinar_secao`, para que a revisão deixe de usar o prompt de geração inicial. No frontend, o `SugestaoIA` guarda o histórico do bloco e envia a tentativa e as últimas sugestões.

Analogia: o plano de adaptação é a "planilha" que um editor faz antes de reescrever os capítulos. Ela diz em quais capítulos cada termo muda. Cada capítulo é reescrito em separado, mas segue a mesma planilha.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Backend (`src/jobsync/curriculo`):

| Componente | Situação | Responsabilidade |
|---|---|---|
| `domain/contexto_vaga.py` → `ContextoVaga` | **Modificado** | Ganha `cargo_alvo: str = ""` |
| `domain/equivalencia_tecnologia.py` → `EquivalenciaTecnologia` | **Novo** | VO `original`, `alvo`; nomes obrigatórios e diferentes |
| `domain/plano_adaptacao.py` → `PlanoAdaptacao`, `DiretrizesExperiencia` | **Novo** | Distribui as trocas entre experiências; expõe diretrizes por índice e a lista de ajustes |
| `domain/identificador_equivalencias_port.py` | **Novo** | Porta que aponta equivalências entre o perfil e a vaga |
| `domain/refino.py` → `FocoRefino`, `PedidoRefino` | **Novo** | Rodízio de focos e histórico de sugestões |
| `domain/ajustador_experiencia_port.py` | **Modificado** | `ajustar(experiencia, contexto, diretrizes)`; `refinar(experiencia, contexto, refino)` |
| `domain/ajustador_texto_port.py` | **Modificado** | `ajustar_secao(secao, contexto, ajustes)`; novo `refinar_secao(secao, contexto, refino)` |
| `domain/melhorador_texto_curriculo_port.py` | **Modificado** | `melhorar_secao` e `melhorar_experiencia` recebem `refino` |
| `domain/rascunho_curriculo_adaptado.py` | **Modificado** | Guarda `ajustes_tecnologia` (tupla de `AjusteTecnologia`) |
| `adapters/identificador_equivalencias_openai_client.py` | **Novo** | Prompt e parse das equivalências |
| `adapters/ajustador_experiencia_openai_client.py` | **Modificado** | Cargo-alvo, diretrizes de troca, responsabilidades implícitas, foco de refino |
| `adapters/ajustador_texto_client.py` | **Modificado** | Cargo-alvo; PERFIL coerente com as trocas; TECNOLOGIAS com original e alvo; `refinar_secao` |
| `adapters/melhorador_texto_curriculo_openai_client.py` | **Modificado** | Foco e sugestões anteriores no prompt |
| `service_layer/adaptar_curriculo_para_vaga/service.py` | **Modificado** | Monta `ContextoVaga`, gera o plano e passa diretrizes |
| `service_layer/sugerir_ajuste_*` (3 casos de uso) | **Modificado** | Recebem `PedidoRefino`; seção com vaga usa `refinar_secao` |
| `entrypoints/api/schemas/curriculo.py` | **Modificado** | `cargo_alvo` em `ContextoVagaSchema`; `refino` nos pedidos; `foco` nas respostas; `ajustes_tecnologia` no rascunho |
| `entrypoints/api/dependencies.py` | **Modificado** | Injeta o identificador |
| `tests/e2e/app_e2e.py` | **Modificado** | Dublês determinísticos do identificador e dos novos parâmetros |

Frontend (`frontend/src`):

| Componente | Situação | Responsabilidade |
|---|---|---|
| `shared/formulario-curriculo/SugestaoIA.tsx` | **Modificado** | Histórico do bloco (até 3), tentativa, exibição do foco |
| `shared/formulario-curriculo/use-sugestoes.ts` | **Modificado** | Envia `refino`; devolve texto e foco |
| `shared/formulario-curriculo/rotulos-foco.ts` | **Novo** | Rótulo em português de cada `FocoRefino` |
| `features/ajustar-vaga/SugestaoExperienciaAdaptada.tsx` | **Modificado** | Envia `refino` |
| `features/ajustar-vaga/AjusteTecnologiaLista.tsx` | **Novo** | Lista "Ajustes de tecnologia" |
| `features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx` | **Modificado** | Lista de ajustes e aviso atualizado |
| `features/ajustar-vaga/AjustarVagaPage.tsx` | **Modificado** | Inclui `cargo_alvo` no `contextoVaga` |
| `api/*` | **Modificado** | Tipos regenerados |

Fluxo da adaptação (fonte estruturada):

```
AdaptarCurriculoParaVaga
  ├─ analisador_vaga.analisar → AnaliseVaga
  ├─ ContextoVaga(descricao, idioma, analise, cargo_alvo)
  ├─ identificador.identificar(experiencias, contexto) → equivalências   (1 chamada de IA)
  ├─ PlanoAdaptacao.distribuir(experiencias, equivalências)              (domínio, sem IA)
  ├─ ajustador_experiencia.ajustar(exp_i, contexto, plano.diretrizes(i)) (1 por experiência)
  └─ ajustador_texto.ajustar_secao(secao, contexto, plano.ajustes)       (1 por seção)
```

## Design de Implementação

### Interfaces Principais

```python
@dataclass(frozen=True)
class EquivalenciaTecnologia:
    original: str
    alvo: str

@dataclass(frozen=True)
class AjusteTecnologia:
    indice_experiencia: int
    equivalencia: EquivalenciaTecnologia

@dataclass(frozen=True)
class DiretrizesExperiencia:
    trocar: tuple[EquivalenciaTecnologia, ...] = ()
    manter: tuple[str, ...] = ()        # originais que esta experiência mantém

@dataclass(frozen=True)
class PlanoAdaptacao:
    ajustes: tuple[AjusteTecnologia, ...]
    manutencoes: tuple[tuple[int, str], ...]

    @classmethod
    def distribuir(cls, experiencias: Sequence[ExperienciaParaAvaliacao],
                   equivalencias: Iterable[EquivalenciaTecnologia]) -> "PlanoAdaptacao": ...
    def diretrizes(self, indice: int) -> DiretrizesExperiencia: ...
    @classmethod
    def vazio(cls) -> "PlanoAdaptacao": ...

class IdentificadorEquivalenciasPort(ABC):
    @abstractmethod
    def identificar(self, experiencias: Sequence[ExperienciaParaAvaliacao],
                    contexto: ContextoVaga) -> tuple[EquivalenciaTecnologia, ...]: ...
```

Regras de `PlanoAdaptacao.distribuir` (todas no domínio, testáveis sem IA):

1. Descarta equivalências cujo `alvo` já aparece em alguma experiência (o candidato já tem a tecnologia).
2. Para cada equivalência, acha as experiências que citam o `original` (comparação por palavra inteira, sem diferenciar maiúsculas, em cargo e descrição).
3. Uma ocorrência: troca nela.
4. Duas ou mais: troca em todas, menos na última da sequência, que mantém a original. A sequência é a ordem recebida do perfil. **Não há ordenação por período hoje** (verifiquei `perfil_estruturado`); a regra assume que o usuário cadastra da mais recente para a mais antiga (questão em aberto 2).
5. Uma experiência pode ter mais de uma troca, de equivalências diferentes.

Refino:

```python
class FocoRefino(str, Enum):
    ADERENCIA_VAGA = "aderencia_vaga"
    IMPACTO = "impacto"
    PALAVRAS_CHAVE = "palavras_chave"
    CLAREZA_CONCISAO = "clareza_concisao"
    ENFASE_TECNICA = "enfase_tecnica"

_RODIZIO_COM_VAGA = (ADERENCIA_VAGA, IMPACTO, PALAVRAS_CHAVE, CLAREZA_CONCISAO)
_RODIZIO_SEM_VAGA = (IMPACTO, CLAREZA_CONCISAO, ENFASE_TECNICA)

@dataclass(frozen=True)
class PedidoRefino:
    tentativa: int = 1                         # >= 1
    sugestoes_anteriores: tuple[str, ...] = () # no máximo 3, cada uma <= LIMITE_CARACTERES_SUGESTAO

    def foco(self, com_vaga: bool) -> FocoRefino:
        rodizio = _RODIZIO_COM_VAGA if com_vaga else _RODIZIO_SEM_VAGA
        return rodizio[(self.tentativa - 1) % len(rodizio)]
```

Portas alteradas (resumo):

```python
class AjustadorExperienciaPort(ABC):
    def ajustar(self, experiencia: ExperienciaParaAvaliacao, contexto: ContextoVaga,
                diretrizes: DiretrizesExperiencia) -> ExperienciaAdaptada: ...
    def refinar(self, experiencia: ExperienciaAdaptada, contexto: ContextoVaga,
                refino: PedidoRefino) -> ExperienciaAdaptada: ...

class AjustadorTextoPort(ABC):
    def ajustar_secao(self, secao: SecaoCurriculo, contexto: ContextoVaga,
                      ajustes: Sequence[EquivalenciaTecnologia] = ()) -> SecaoCurriculo: ...
    def refinar_secao(self, secao: SecaoCurriculo, contexto: ContextoVaga,
                      refino: PedidoRefino) -> SecaoCurriculo: ...
```

Os casos de uso de sugestão devolvem o resultado junto com o foco usado (`SugestaoRefinada[T]` com `valor: T` e `foco: FocoRefino`), para a API repassá-lo ao frontend.

### Regras dos prompts

`AjustadorExperienciaOpenAIClient` (`ajustar` e `refinar`):

- Recebe o cargo-alvo: "Use o cargo-alvo para escolher ênfase e vocabulário."
- Responsabilidades implícitas: "Se a vaga exigir uma responsabilidade comum ao cargo desta experiência e ela não estiver no texto, cite-a em uma conquista ou no contexto. Não cite responsabilidades atípicas para o cargo. Não invente métricas para elas."
- Com `diretrizes.trocar`: "Nesta experiência, use {alvo} no lugar de {original} e cite {alvo} de forma explícita no contexto."
- Com `diretrizes.manter`: "Mantenha {original} e cite-o de forma explícita no contexto."
- A regra atual "sem inventar tecnologias" passa a ser: "Não acrescente tecnologias além das que estão no texto e das trocas indicadas."
- `refinar`: "Parta do texto atual. Foco desta versão: {descrição do foco}. Não repita estas versões: {anteriores}." A experiência da revisão já traz as trocas no texto, então `refinar` as mantém por instrução ("mantenha as tecnologias citadas").

`AjustadorTextoClient`:

- Todas as seções recebem o cargo-alvo.
- `TECNOLOGIAS`: com `ajustes`, "liste também {alvo} ao lado de {original}". A regra atual já mantém todas as originais.
- `PERFIL`: "Pode citar {alvo} quando estiver na lista de ajustes." Também corrige a instrução atual, que proíbe tecnologias novas no resumo e conflita com a instrução geral do prompt de usuário ("inclua explicitamente todas as tecnologias").
- `refinar_secao`: prompt próprio, com "Texto atual" no lugar de "Conteúdo original", foco e anteriores.

`MelhoradorTextoCurriculoOpenAIClient`: mesmo bloco de foco e anteriores, sem vaga.

`IdentificadorEquivalenciasOpenAIClient`: recebe as descrições das experiências e os requisitos explícitos e implícitos da análise. Responde `{"equivalencias": [{"original": "React", "alvo": "Angular"}]}`. Regras: mesma categoria, `original` presente no texto, `alvo` presente na vaga. Formato inválido levanta `ValueError`.

### Modelos de Dados

Sem banco de dados. Mudanças de contrato:

```json
// ContextoVagaSchema (pedidos de sugestão)
{"descricao_vaga": "...", "idioma_alvo": "pt", "analise_vaga": {...},
 "cargo_alvo": "Desenvolvedor Full Stack"}          // novo, opcional, padrão ""

// Pedidos de sugestão (seção, experiência do perfil, experiência adaptada)
{"...": "...", "refino": {"tentativa": 2, "sugestoes_anteriores": ["..."]}}  // novo, opcional

// Respostas de sugestão
{"...": "...", "foco": "impacto"}                     // novo

// RascunhoAdaptadoResponse.rascunho
{"...": "...", "ajustes_tecnologia": [
  {"indice_experiencia": 0, "cargo": "Dev Full Stack", "empresa": "X",
   "original": "React", "alvo": "Angular"}]}          // novo, lista vazia por padrão
```

`ajustes_tecnologia` é só informativo. O `POST /v1/curriculos-revisados` não o recebe nem o valida.

### Endpoints de API

| Método e caminho | Situação | Mudança |
|---|---|---|
| `POST /v1/curriculos/{id}/rascunhos-adaptados` | Compatível | Resposta ganha `ajustes_tecnologia` |
| `POST /v1/secoes-curriculo/sugestoes` | Compatível | `refino` opcional; `contexto_vaga.cargo_alvo` opcional; resposta com `foco` |
| `POST /v1/experiencias-profissionais/sugestoes` | Compatível | `refino` opcional (o schema usa `extra="forbid"`; o campo precisa ser declarado); resposta com `foco` |
| `POST /v1/experiencias-adaptadas/sugestoes` | Compatível | `refino` e `cargo_alvo` opcionais; resposta com `foco` |
| `POST /v1/curriculos/{id}/adaptacoes` | Inalterado | O PDF já reflete as trocas |

Atualizar `job-sync.postman_collection.json` e regenerar `schema.d.ts` com Python 3.12, como na JOB-0035.

## Pontos de Integração

OpenAI, pelo `ClienteOpenAI` atual. Uma chamada a mais por adaptação (identificador). Falha do identificador **não** interrompe a adaptação: o caso de uso registra `WARNING` e usa `PlanoAdaptacao.vazio()`. Nas sugestões, erros seguem o padrão `SugestaoIAIndisponivel` → 502.

## Abordagem de Testes

TDD, conforme `.windsurf/rules/testing-rules.md`.

### Testes Unidade

Backend:

- `PlanoAdaptacao.distribuir`: uma ocorrência troca; duas ocorrências trocam na primeira e mantêm na última; três ocorrências mantêm só a última; `alvo` já presente descarta a troca; comparação por palavra inteira ("Java" não casa com "JavaScript"); experiência sem descrição fica sem diretrizes; duas equivalências na mesma experiência.
- `PedidoRefino`: rodízio com e sem vaga; tentativa menor que 1 e mais de 3 anteriores levantam `ValueError`.
- `ContextoVaga`: `cargo_alvo` opcional e aparado.
- Adapters (mock do `ClienteOpenAI`): o prompt contém cargo-alvo, a regra de responsabilidades implícitas, a instrução de troca e de manutenção, o foco e as anteriores; parse e erros do identificador.
- `AjustadorTextoClient`: TECNOLOGIAS cita original e alvo; `refinar_secao` usa "Texto atual" e não "Conteúdo original".
- `AdaptarCurriculoParaVaga`: cada experiência recebe suas diretrizes; o rascunho traz os ajustes; falha do identificador gera plano vazio.
- Casos de uso de sugestão: repassam `refino` e devolvem o foco; seção com vaga chama `refinar_secao`.
- Schemas e routers: campos novos opcionais; pedidos antigos continuam válidos; `foco` nas respostas.

Frontend (Vitest):

- `SugestaoIA`: o segundo pedido envia tentativa 2 e a sugestão anterior; guarda no máximo 3; mostra o foco; o pedido usa o texto atual do campo.
- `AjusteTecnologiaLista`: lista as trocas; não aparece sem trocas.
- `AjustarVagaPage`: `contextoVaga` inclui `cargo_alvo`.

### Testes de Serviço

E2E (Playwright), com dublês determinísticos: revisão mostra a lista de ajustes; dois pedidos seguidos mostram focos diferentes; acessibilidade (axe) com a lista e o foco.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. `ContextoVaga` com `cargo_alvo` e refatoração das portas para receber `ContextoVaga` (sem mudar comportamento). Base de tudo.
2. `EquivalenciaTecnologia`, `PlanoAdaptacao` e testes de distribuição.
3. `IdentificadorEquivalenciasPort` e adapter.
4. Diretrizes no `AjustadorExperienciaOpenAIClient` e ajustes no `AjustadorTextoClient`; integração em `AdaptarCurriculoParaVaga`.
5. `FocoRefino`, `PedidoRefino`, `refinar_secao` e foco nos três casos de uso de sugestão.
6. Schemas, routers, injeção, Postman e tipos do frontend.
7. `SugestaoIA` com histórico e foco; `use-sugestoes`.
8. Revisão: lista de ajustes, aviso e `cargo_alvo` no contexto.
9. E2E, acessibilidade e suíte completa.

### Dependências Técnicas

Nenhuma bloqueante. JOB-0034 e JOB-0035 já estão na `main`.

## Monitoramento e Observabilidade

- `INFO` na adaptação: quantidade de equivalências apontadas, de trocas e de manutenções. Sem nomes de tecnologias associados a pessoa ou empresa.
- `INFO` na sugestão: o registro atual (`registrar_sugestao`) ganha `tentativa` e `foco`.
- `WARNING` quando o identificador falhar ou responder fora do formato (só o tipo do erro).

## Considerações Técnicas

### Decisões Principais

1. **Distribuição no domínio, equivalência na IA.** A IA sabe o que é equivalente; a regra "não trocar em todas" é de negócio e precisa ser previsível. Alternativa rejeitada: pedir a distribuição no prompt de cada experiência. As chamadas são independentes e não enxergam as outras experiências.
2. **Uma chamada para equivalências.** Mantém as chamadas por experiência simples. Trade-off: uma chamada a mais por adaptação. Alternativa rejeitada: tabela fixa de equivalências (não cobre a variedade de tecnologias e exige manutenção).
3. **Portas recebem `ContextoVaga`.** Evita somar um quarto parâmetro solto a cada porta (DRY). Trade-off: muda assinaturas e dublês de teste existentes.
4. **Foco em rodízio pela tentativa.** Determinístico e testável. Alternativa rejeitada: aumentar a temperatura do modelo (o `ClienteOpenAI` não a define hoje, e a variação ficaria aleatória e sem garantia de mudança de abordagem).
5. **Histórico no frontend.** O backend segue sem estado. O frontend já guarda o rascunho na sessão da tela.
6. **`ajustes_tecnologia` só informativo.** Se o usuário editar o texto e desfizer a troca, a lista fica desatualizada. Aceito: ela descreve o que a IA fez, não o estado atual.

### Riscos Conhecidos

- **Ética e entrevista:** a troca coloca no currículo uma tecnologia que o candidato não usou naquela empresa. É decisão de produto. A mitigação é a lista de ajustes e o aviso na revisão.
- **Equivalência errada:** a IA pode apontar pares de categorias diferentes. Mitigação: regra no prompt e a lista visível para o usuário. Não validei a qualidade com o modelo real.
- **Ordem das experiências:** sem ordenação por período, "mais recente" depende do cadastro do usuário.
- **Repetição apesar do foco:** o modelo pode devolver texto parecido com um anterior. Mitigação: enviar as anteriores. Não há verificação automática de similaridade nesta JOB.
- **Custo:** a lista de anteriores aumenta o prompt. Limite de 3 itens, cada um dentro de `LIMITE_CARACTERES_SUGESTAO`.

### Conformidade com Padrões

- `code-design-standards.md`: VOs e portas em `curriculo/domain`, sem infraestrutura; adapters em `curriculo/adapters`; casos de uso com `executar` e injeção por construtor.
- `back-end-general-rules.md`: só campos novos opcionais nos pedidos e campos novos nas respostas; sem quebra de contrato. 200, 422 e 502 como hoje.
- `testing-rules.md`: `Test<Classe>`, AAA, mocks só para portas e `ClienteOpenAI`.
- `general-rules.md` e `AGENTS.md`: Tell Don't Ask (`PlanoAdaptacao.diretrizes`, `PedidoRefino.foco`), DRY (`ContextoVaga`), hexagonal, TDD.
- Nenhum desvio identificado.

### Arquivos relevantes e dependentes

- `src/jobsync/curriculo/domain/{contexto_vaga.py,ajustador_experiencia_port.py,ajustador_texto_port.py,melhorador_texto_curriculo_port.py,rascunho_curriculo_adaptado.py}`
- `src/jobsync/curriculo/adapters/{ajustador_experiencia_openai_client.py,ajustador_texto_client.py,melhorador_texto_curriculo_openai_client.py}`
- `src/jobsync/curriculo/service_layer/{adaptar_curriculo_para_vaga,sugerir_ajuste_experiencia,sugerir_ajuste_experiencia_adaptada,sugerir_ajuste_secao_curriculo}/`, `validacoes_sugestao.py`
- `src/jobsync/entrypoints/api/{schemas/curriculo.py,routers/curriculo_router.py,dependencies.py}`
- `src/jobsync/entrypoints/streamlit_app.py` (chama `AdaptarCurriculoParaVaga`; só precisa da injeção nova)
- `src/jobsync/tests/e2e/app_e2e.py`, `tests/curriculo/*`, `tests/entrypoints/api/*`
- `frontend/src/shared/formulario-curriculo/*`, `frontend/src/features/ajustar-vaga/*`, `frontend/src/features/perfil/PerfilPage.tsx`, `frontend/src/api/*`, `frontend/e2e/*`
- `job-sync.postman_collection.json`

## Questões em Aberto

1. Regra de distribuição: "todas menos a mais antiga" (proposta) ou "metade mais recente"?
2. Ordenar as experiências por período no domínio, ou confiar na ordem do cadastro?
3. Trocar também na fonte PDF, só por instrução no prompt (sem garantia)?
4. Comparar similaridade entre sugestões e pedir nova versão quando forem quase iguais (custo de uma chamada extra)?

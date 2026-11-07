# Especificação Técnica — JOB-0035

PRD de referência: `prd-job-0035.md` (mesmo diretório).
Depende de: JOB-0033 e JOB-0034 (PR 45). Este trabalho altera contratos que essas JOBs criaram e que ainda não foram publicados.

## Resumo Executivo

Cada experiência adaptada passa a ser um modelo de domínio próprio, `ExperienciaAdaptada` (cargo, empresa, período, conquistas e contexto). A porta `AjustadorExperienciaPort` devolve esse modelo e ganha o método `refinar`, usado pelas sugestões da revisão. O agregado `RascunhoCurriculoAdaptado` guarda `ExperienciaAdaptada` no lugar da descrição em texto.

O `Curriculo` e o gerador de PDF continuam baseados em texto. Por isso a conversão rascunho → `Curriculo` monta a seção de experiências com uma convenção: cabeçalho, bullets iniciados por "-" e uma linha final "Contexto:" ou "Context:". O gerador de PDF reconhece essa linha e a desenha em itálico cinza. Essa mesma convenção serve às duas fontes: a estruturada, que gera o texto a partir dos campos, e a de PDF, em que a IA escreve o texto direto.

No frontend, a revisão troca o campo "Descrição" por "Conquistas" (uma por linha) e "Contexto". O `SugestaoIA` fica genérico no tipo da sugestão, para aplicar conquistas e contexto de uma vez.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Backend (`src/jobsync`):

| Componente | Situação | Responsabilidade |
|---|---|---|
| `curriculo/domain/experiencia_adaptada.py` → `ExperienciaAdaptada` | **Novo** | VO com invariantes; gera o texto de PDF e o texto para avaliação |
| `curriculo/domain/rotulos_experiencia.py` | **Novo** | Rótulo do contexto por idioma (`Contexto`, `Context`) e o conjunto de rótulos reconhecidos |
| `curriculo/domain/rascunho_curriculo_adaptado.py` | **Modificado** | Guarda `ExperienciaAdaptada`; `para_curriculo(idioma_alvo)` |
| `curriculo/domain/ajustador_experiencia_port.py` | **Modificado** | `ajustar` e `refinar` devolvem `ExperienciaAdaptada` |
| `curriculo/adapters/ajustador_experiencia_openai_client.py` | **Modificado** | Prompt e parse do formato conquistas + contexto |
| `curriculo/adapters/ajustador_texto_client.py` | **Modificado** | Prompt da seção EXPERIENCIAS (fonte PDF) com a convenção de texto |
| `curriculo/adapters/gerador_pdf_client.py` | **Modificado** | Estilo e reconhecimento da linha de contexto |
| `curriculo/service_layer/adaptar_curriculo_para_vaga/` | **Modificado** | Usa `ExperienciaAdaptada`; avalia o texto composto |
| `curriculo/service_layer/gerar_pdf_curriculo_revisado/` | **Modificado** | Passa o idioma alvo a `para_curriculo` |
| `curriculo/service_layer/sugerir_ajuste_experiencia_adaptada/` | **Novo** | Caso de uso `SugerirAjusteExperienciaAdaptada` (com vaga, via `refinar`) |
| `curriculo/service_layer/sugerir_ajuste_experiencia/` | **Modificado** | Fica só com o modo "Meu perfil": remove a ramificação com vaga |
| `entrypoints/api/schemas/curriculo.py` | **Modificado** | `ExperienciaRascunhoSchema` com `conquistas` e `contexto`; schemas da nova sugestão; remove `contexto_vaga` do pedido de experiência do perfil |
| `entrypoints/api/routers/curriculo_router.py`, `dependencies.py` | **Modificado** | Novo endpoint e injeção |
| `tests/e2e/app_e2e.py` | **Modificado** | Dublês de `ajustar` e `refinar` |

Frontend (`frontend/src`):

| Componente | Situação | Responsabilidade |
|---|---|---|
| `shared/formulario-curriculo/campos-curriculo.ts` | **Modificado** | `ExperienciaAdaptadaFormulario`, `CAMPOS_EXPERIENCIA_ADAPTADA` |
| `shared/formulario-curriculo/SugestaoIA.tsx` | **Modificado** | Genérico: `sugerir` devolve `S`, com `descrever(S)` e `aplicar(S)` |
| `shared/formulario-curriculo/SugestaoCampo.tsx` | **Modificado** | Usa o `SugestaoIA` genérico com `S = string` |
| `features/ajustar-vaga/SugestaoExperienciaAdaptada.tsx` | **Novo** | Sugestão da experiência: lê e grava conquistas e contexto |
| `features/ajustar-vaga/formulario-revisao.ts` | **Modificado** | Mapeia lista ↔ linhas; compõe o texto para avaliação |
| `features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx` | **Modificado** | Campos novos, aviso de números estimados, nova sugestão |
| `shared/formulario-curriculo/use-sugestoes.ts` | **Modificado** | `experienciaAdaptada` (com vaga); `experiencia` fica só sem vaga |
| `api/*` | **Modificado** | `sugerirAjusteExperienciaAdaptada` e tipos regenerados |

## Design de Implementação

### Interfaces Principais

```python
@dataclass(frozen=True)
class ExperienciaAdaptada:
    cargo: str
    empresa: str
    periodo: str
    conquistas: tuple[str, ...]
    contexto: str = ""
    # __post_init__: cargo e empresa obrigatórios; conquistas sem itens em branco.

    @classmethod
    def revisada(cls, cargo, empresa, periodo, conquistas: Iterable[str], contexto) -> "ExperienciaAdaptada":
        """Aparas e descarta conquistas em branco (edição do usuário)."""
    def para_texto(self, rotulo_contexto: str) -> str:
        """'Cargo — Empresa (Período)' + '- conquista' por linha + 'Rótulo: contexto'."""
    def para_avaliacao(self) -> ExperienciaParaAvaliacao:
        """Mesma descrição sem cabeçalho e sem rótulo, para o avaliador Jev."""

class AjustadorExperienciaPort(ABC):
    def ajustar(self, experiencia: ExperienciaParaAvaliacao, descricao_vaga: str,
                idioma_alvo: str, analise_vaga: AnaliseVaga) -> ExperienciaAdaptada: ...
    def refinar(self, experiencia: ExperienciaAdaptada, descricao_vaga: str,
                idioma_alvo: str, analise_vaga: AnaliseVaga) -> ExperienciaAdaptada: ...
```

Regras do domínio:

- `para_texto` usa o formato atual do cabeçalho; a seção `EXPERIENCIAS` é montada com blocos separados por linha em branco. Sem conquistas e sem contexto, o bloco traz só o cabeçalho.
- `RascunhoCurriculoAdaptado.para_curriculo(idioma_alvo)` escolhe o rótulo em `ROTULO_CONTEXTO` (`pt` → "Contexto", `en` → "Context"). A assinatura não tem valor padrão, para ninguém esquecer o idioma.
- `revisado()` do rascunho descarta experiências totalmente em branco. A validação de cargo e empresa passa para `ExperienciaAdaptada`.

Prompt do adapter `ajustar` e `refinar` (`AjustadorExperienciaOpenAIClient`):

- Gerar de 2 a 6 conquistas, cada uma uma frase curta no idioma alvo, começando por verbo de ação, com o resultado medido quando houver dado.
- Gerar um contexto de 1 a 3 frases sobre a empresa, a área e o papel, sem repetir as conquistas.
- Preferir os números da fonte. Quando a fonte não tiver número, **pode** propor métricas e volumes plausíveis e conservadores (decisão de produto, PRD RF6).
- Não alterar cargo, empresa nem período.
- Resposta somente em JSON: `{"conquistas": ["..."], "contexto": "..."}`. Conquistas vazias ou fora de lista levantam `ValueError`.

Prompt de `AjustadorTextoClient` para `EXPERIENCIAS` (fonte PDF): manter o cabeçalho de cada experiência, listar bullets com "-" e terminar cada bloco com a linha "Contexto: ..." ou "Context: ..." conforme o idioma. Mesma regra de métricas.

Gerador de PDF (`GeradorPdfClient._formatar_conteudo_experiencias`): antes das regras de índice, uma linha que comece com um rótulo reconhecido (sem diferenciar maiúsculas) é desenhada com o novo estilo `contexto` (`Helvetica-Oblique`, cor `#666666`), com o rótulo incluído. A verificação precisa vir **antes** do ramo `index == 1 and _parece_posicao_experiencia`, que hoje poria em negrito um contexto curto sem ano logo após o cabeçalho.

Casos de uso:

```python
class SugerirAjusteExperienciaAdaptada:
    def __init__(self, ajustador_experiencia: AjustadorExperienciaPort) -> None: ...
    def executar(self, experiencia: ExperienciaAdaptada, contexto: ContextoVaga) -> ExperienciaAdaptada: ...
```

- Valida que há ao menos uma conquista ou um contexto e que o texto total respeita `LIMITE_CARACTERES_SUGESTAO`. Falha da porta vira `SugestaoIAIndisponivel`.
- `SugerirAjusteExperiencia` (JOB-0034) perde `AjustadorExperienciaPort` e o parâmetro `contexto`: serve só a "Meu perfil", com o `MelhoradorTextoCurriculoPort`.

Componente genérico (frontend):

```ts
interface SugestaoIAProps<S> {
  rotuloBloco: string; textoAtual: string;
  sugerir: (texto: string) => Promise<S>;
  descrever: (sugestao: S) => string;   // texto do painel
  aplicar: (sugestao: S) => void; focarCampo?: () => void;
}
```

### Modelos de Dados

Sem banco de dados. `ExperienciaRascunhoSchema`:

```json
{"cargo": "Dev Backend", "empresa": "TechCorp", "periodo": "2022 - Atual",
 "conquistas": ["Desenvolvi faturamento VoIP de 5.000 bilhetes por minuto, com processamento em lote."],
 "contexto": "Na TechCorp, líder em telecom, atuei na plataforma de comunicação usada diariamente por milhares de pessoas."}
```

Formulário da revisão: `conquistas` é um texto com uma conquista por linha. Ao mapear, o texto é dividido por linha, aparado, sem linhas em branco. A avaliação ("Avaliar") recebe `descricaoParaAvaliacao`, a mesma composição de `para_avaliacao()` feita no frontend.

### Endpoints de API

| Método e caminho | Situação | Descrição |
|---|---|---|
| `POST /v1/curriculos/{id}/rascunhos-adaptados` | **Contrato muda** | `rascunho.experiencias[]` troca `descricao` por `conquistas` e `contexto` |
| `POST /v1/curriculos-revisados` | **Contrato muda** | Mesmo formato de experiência no corpo |
| `POST /v1/experiencias-adaptadas/sugestoes` | **Novo** | Corpo: `experiencia` (cargo, empresa, período, conquistas, contexto) e `contexto_vaga` obrigatório. Resposta: `conquistas` e `contexto`. 200, 422, 502 |
| `POST /v1/experiencias-profissionais/sugestoes` | **Contrato muda** | Perde `contexto_vaga`; só o modo "Meu perfil" |
| `POST /v1/curriculos/{id}/adaptacoes` | Contrato JSON inalterado | O PDF muda de aparência; o `curriculo_adaptado` passa o idioma a `para_curriculo` |

Atualizar `job-sync.postman_collection.json` e regenerar `schema.d.ts` **com Python 3.12**, o mesmo do CI (com 3.13, a descrição padrão do 422 muda e o passo de contrato falha).

## Pontos de Integração

OpenAI, pelo `ClienteOpenAI` já usado. Sem credencial nova. Erros do provedor seguem o padrão: `SugestaoIAIndisponivel` → 502.

## Abordagem de Testes

TDD, conforme `.windsurf/rules/testing-rules.md`.

### Testes Unidade

Backend:

- `ExperienciaAdaptada`: invariantes, `revisada`, `para_texto` (com e sem conquistas, sem contexto, por idioma) e `para_avaliacao`.
- Rascunho: `para_curriculo(idioma)` monta a seção; experiências em branco são descartadas.
- Adapter: prompt com as regras (verbo de ação, números da fonte, estimativa conservadora, preservar cargo, empresa e período); parse do JSON; JSON inválido, lista vazia e item em branco levantam erro (mock do `ClienteOpenAI`).
- `AjustadorTextoClient`: o prompt de EXPERIENCIAS menciona a convenção de bullets e de linha de contexto.
- Gerador de PDF, com `pdfplumber`: o contexto sai com fonte oblíqua e cor cinza, depois dos bullets; contexto logo após o cabeçalho não vira negrito; sem conquistas ou sem contexto não deixa linhas ou rótulos soltos.
- `SugerirAjusteExperienciaAdaptada`: chama `refinar` com o texto recebido; limite de tamanho; falha vira 502. `SugerirAjusteExperiencia` só delega ao melhorador.
- `AdaptarCurriculoParaVaga`: o rascunho traz `ExperienciaAdaptada` e a avaliação recebe o texto composto.
- Routers e schemas: novo endpoint (200, 422, 502); formato novo do rascunho e do PDF revisado; o pedido de experiência do perfil rejeita `contexto_vaga`.

Frontend (Vitest):

- `formulario-revisao`: ida e volta lista ↔ linhas; composição para avaliação.
- `SugestaoIA` genérico: os testes atuais passam com `S = string`; um caso com `S` estruturado.
- Revisão: campos "Conquistas" e "Contexto", aviso de números estimados (só com experiências estruturadas), sugestão aplica os dois campos, "Avaliar" recebe o texto composto.

### Testes de Serviço

E2E (Playwright): revisar conquistas e contexto, pedir e aplicar a sugestão, baixar o PDF. Acessibilidade com o aviso e os campos novos. Os dublês de IA do `app_e2e.py` seguem determinísticos.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. `ExperienciaAdaptada`, rótulos e refatoração do rascunho. Base de tudo.
2. Porta (`ajustar`, `refinar`), adapter e `AdaptarCurriculoParaVaga`.
3. Gerador de PDF (estilo e reconhecimento) e prompt do `AjustadorTextoClient`.
4. `SugerirAjusteExperienciaAdaptada` e simplificação de `SugerirAjusteExperiencia`.
5. Schemas, endpoints, injeção e Postman.
6. Cliente de API e tipos do frontend (contrato com Python 3.12).
7. `SugestaoIA` genérico, campos e mapeamento do formulário.
8. Tela de revisão: campos, aviso e sugestão da experiência.
9. E2E, acessibilidade e suíte completa.

### Dependências Técnicas

Bloqueante: o PR 45 (JOB-0033 e JOB-0034). A branch desta JOB parte da branch desse PR.

## Monitoramento e Observabilidade

- `INFO` ao gerar o rascunho e a sugestão: contagem de conquistas por experiência e tamanhos, sem conteúdo.
- `WARNING` quando o JSON do modelo vier fora do formato (tipo do erro, sem texto).
- Nunca registrar conquistas, contexto, nome ou descrição da vaga.

## Considerações Técnicas

### Decisões Principais

1. **Campos estruturados no domínio, convenção de texto no PDF.** O `Curriculo` e o gerador seguem baseados em texto, e mudar isso exigiria reescrever o gerador. Trade-off: o reconhecimento da linha de contexto depende do rótulo. Alternativa rejeitada: dar a `SecaoCurriculo` uma lista de itens estruturados (escopo maior, sem ganho para o usuário).
2. **`refinar` na porta existente.** Reaproveita o adapter e o prompt do mesmo formato. Alternativa rejeitada: uma segunda porta só para sugestões.
3. **Endpoint próprio para a sugestão estruturada.** O contrato de texto livre de "Meu perfil" e o de conquistas e contexto da revisão têm formas diferentes. Misturá-los exigiria campos opcionais cruzados.
4. **Campo de texto com uma conquista por linha.** Um campo por conquista seria mais caro de construir e testar. Fica como evolução.
5. **Aviso fixo de números estimados.** Fácil de manter e não depende de o modelo marcar as próprias estimativas. Trade-off: o aviso aparece mesmo quando não houve estimativa.

### Riscos Conhecidos

- **Métricas estimadas:** o usuário pode enviar números que não são dele. A decisão é do produto, e a proteção é o aviso e a etapa de revisão. É uma regra oposta à do prompt atual ("não invente métricas") e à do PRD da JOB-0034 (RF6). Os dois textos precisam ser atualizados nesta JOB.
- **Convenção de texto na fonte PDF:** se a IA omitir o rótulo, o PDF mostra a linha comum, sem itálico. Mitigação: instruir o formato no prompt e testá-lo; não há garantia do modelo. Não validei isso com a IA real.
- **Quebra de contrato das JOBs 0033 e 0034:** seguro só enquanto o PR 45 não for usado por outro cliente. Se for integrado antes, tornar a mudança compatível (aceitar `descricao` legada).
- **Duplicação da composição de texto:** backend (`para_avaliacao`) e frontend (`descricaoParaAvaliacao`) formam o mesmo texto. Mitigação: casos de teste idênticos nos dois lados.
- **Cinza no PDF:** `#666666` sobre branco tem contraste de cerca de 5,7:1 (cálculo meu, não medido em impressão).

### Conformidade com Padrões

- `code-design-standards.md`: VO e porta em `curriculo/domain`, sem infraestrutura; adapters em `curriculo/adapters`; casos de uso em pacotes por funcionalidade com `executar` e injeção por construtor; um service não chama outro.
- `back-end-general-rules.md`: recurso no plural (`experiencias-adaptadas`), POST para ação não-CRUD, 200 sem persistência, 422 e 502. **Desvio documentado:** a regra pede não alterar contratos sem pedido. Aqui há pedido explícito, e os contratos alterados pertencem ao PR 45, ainda aberto.
- `testing-rules.md`: `Test<Classe>`, AAA, sem comentários, mocks só para portas e cliente de IA.
- `AGENTS.md`: DRY (os rótulos e a composição ficam em um só lugar de cada lado), Tell Don't Ask (`para_texto`, `para_avaliacao`), hexagonal e TDD.

### Arquivos relevantes e dependentes

- `src/jobsync/curriculo/domain/{avaliacao_experiencia.py,rascunho_curriculo_adaptado.py,ajustador_experiencia_port.py}`
- `src/jobsync/curriculo/adapters/{ajustador_experiencia_openai_client.py,ajustador_texto_client.py,gerador_pdf_client.py}`
- `src/jobsync/curriculo/service_layer/{adaptar_curriculo_para_vaga,gerar_pdf_curriculo_revisado,sugerir_ajuste_experiencia}/`
- `src/jobsync/entrypoints/api/{routers/curriculo_router.py,schemas/curriculo.py,dependencies.py}`
- `src/jobsync/tests/e2e/app_e2e.py`, `tests/curriculo/*`, `tests/entrypoints/api/*`
- `frontend/src/shared/formulario-curriculo/*`, `frontend/src/features/ajustar-vaga/*`, `frontend/src/api/*`, `frontend/e2e/*`
- `job-sync.postman_collection.json`

## Questões em Aberto

1. Faixa de conquistas por experiência: usar de 2 a 6 (proposta) ou apenas "ao menos uma"?
2. Remover de vez o `contexto_vaga` de `/experiencias-profissionais/sugestoes`, como proposto, ou manter o campo sem uso por compatibilidade?
3. Para a fonte PDF, o padrão por convenção de texto é suficiente, ou a JOB deve restringir-se à fonte estruturada?

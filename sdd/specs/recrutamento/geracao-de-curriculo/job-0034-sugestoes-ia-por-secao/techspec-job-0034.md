# Especificação Técnica — JOB-0034

PRD de referência: `prd-job-0034.md` (mesmo diretório).
Depende de: `../job-0033-revisao-curriculo-adaptado-antes-do-pdf/techspec-job-0033.md`.

## Resumo Executivo

As sugestões por seção reaproveitam as duas portas de IA que a adaptação já usa: `AjustadorTextoPort.ajustar_secao` (seções de texto) e `AjustadorExperienciaPort.ajustar` (uma experiência). Hoje elas só rodam em lote dentro de `AdaptarCurriculoParaVaga`. Esta spec as expõe em dois casos de uso pontuais e sem estado, um por recurso: `SugerirAjusteSecaoCurriculo` e `SugerirAjusteExperiencia`. Para a tela "Meu perfil", que não tem vaga, entra uma porta nova, `MelhoradorTextoCurriculoPort`, com um adapter OpenAI. Cada caso de uso escolhe a porta conforme a presença do contexto da vaga.

Para não analisar a vaga de novo a cada clique, a resposta do rascunho (JOB-0033) passa a incluir a `analise_vaga`. O frontend a guarda junto com o rascunho e a reenvia em cada pedido de sugestão. No frontend, um componente compartilhado, `SugestaoIA`, recebe por propriedade a função que busca a sugestão (padrão Strategy). Assim, os blocos de `shared/formulario-curriculo` não sabem se estão na revisão ou no perfil.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Backend (`src/jobsync`):

| Componente | Tipo | Situação | Responsabilidade |
|---|---|---|---|
| `curriculo/domain/melhorador_texto_curriculo_port.py` → `MelhoradorTextoCurriculoPort` | Porta | **Nova** | Melhorar a escrita de uma seção ou experiência sem vaga |
| `curriculo/adapters/melhorador_texto_curriculo_openai_client.py` | Adapter | **Novo** | Implementa a porta com `ClienteOpenAI` |
| `curriculo/domain/contexto_vaga.py` → `ContextoVaga` | Value Object | **Novo** | Agrupa `descricao_vaga`, `idioma_alvo` e `analise_vaga` |
| `curriculo/service_layer/sugerir_ajuste_secao_curriculo/` → `SugerirAjusteSecaoCurriculo` | Caso de uso | **Novo** | Sugestão para uma seção de texto |
| `curriculo/service_layer/sugerir_ajuste_experiencia/` → `SugerirAjusteExperiencia` | Caso de uso | **Novo** | Sugestão para uma experiência |
| `curriculo/service_layer/sugestao_ia_indisponivel.py` → `SugestaoIAIndisponivel` | Exceção | **Nova** | Falha do provedor de IA → 502 |
| `entrypoints/api/schemas/vaga.py` → `AnaliseVagaSchema` | Schema | **Novo** | Serializa `AnaliseVaga` (ida e volta) |
| `entrypoints/api/schemas/curriculo.py` | Schemas | **Modificado** | Schemas de sugestão; `RascunhoAdaptadoResponse` ganha `analise_vaga` |
| `entrypoints/api/routers/curriculo_router.py` | Router | **Modificado** | 2 endpoints novos |
| `entrypoints/api/dependencies.py` | DI | **Modificado** | Registra os dois casos de uso |
| `entrypoints/api/exceptions.py` | Handlers | **Modificado** | `SugestaoIAIndisponivel` → 502 |

Frontend (`frontend/src`):

| Componente | Situação | Responsabilidade |
|---|---|---|
| `shared/formulario-curriculo/SugestaoIA.tsx` (+ `.module.css`) | **Novo** | Botão, estado de carregamento, painel "Sugestão da IA" com Aplicar/Descartar, erro |
| `shared/formulario-curriculo/PainelDadosPessoais.tsx` | **Modificado** | Propriedade opcional `sugerirResumo` |
| `shared/formulario-curriculo/ListaItensCurriculo.tsx` | **Sem mudança** | O botão entra pelo `acoesItem` já existente |
| `features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx` | **Modificado** | Liga sugestões com contexto da vaga (resumo, tecnologias, experiências) |
| `features/ajustar-vaga/use-sugestoes-revisao.ts` | **Novo** | Funções de sugestão com `ContextoVaga` |
| `features/perfil/PerfilPage.tsx` | **Modificado** | Liga sugestões sem vaga (resumo, experiências) |
| `features/perfil/use-perfil-estruturado.ts` | **Modificado** | Funções de sugestão sem vaga |
| `api/api-client.ts`, `http-api-client.ts`, `tipos.ts`, `schema.d.ts` | **Modificado** | `sugerirAjusteSecao`, `sugerirAjusteExperiencia` (com `ia: true`, que usa o timeout de IA) |

Fluxo de dados:

```
Bloco do formulário ──(texto atual do campo)──▶ SugestaoIA.sugerir()
   │  revisão: + contexto_vaga (descrição, idioma, analise_vaga guardada com o rascunho)
   ▼
POST /secoes-curriculo/sugestoes        ──▶ SugerirAjusteSecaoCurriculo
POST /experiencias-profissionais/sugestoes ──▶ SugerirAjusteExperiencia
        com contexto → AjustadorTextoPort / AjustadorExperienciaPort (já existem)
        sem contexto → MelhoradorTextoCurriculoPort (novo)
   ▼
painel "Sugestão da IA" ── Aplicar ──▶ form.setValue(campo, sugestão, { shouldDirty: true })
```

## Design de Implementação

### Interfaces Principais

Value Object (`curriculo/domain/contexto_vaga.py`):

```python
@dataclass(frozen=True)
class ContextoVaga:
    descricao_vaga: str
    idioma_alvo: str
    analise_vaga: AnaliseVaga
    # __post_init__: descrição obrigatória; idioma em {"pt", "en"}
```

Porta nova (`curriculo/domain/melhorador_texto_curriculo_port.py`):

```python
class MelhoradorTextoCurriculoPort(ABC):
    """Melhora a escrita sem vaga-alvo, mantendo idioma e fatos do texto."""
    @abstractmethod
    def melhorar_secao(self, secao: SecaoCurriculo) -> SecaoCurriculo: ...
    @abstractmethod
    def melhorar_experiencia(self, experiencia: ExperienciaParaAvaliacao) -> ExperienciaParaAvaliacao: ...
```

Casos de uso:

```python
class SugerirAjusteSecaoCurriculo:
    def __init__(self, ajustador_texto: AjustadorTextoPort,
                 melhorador: MelhoradorTextoCurriculoPort) -> None: ...
    def executar(self, secao: SecaoCurriculo, contexto: ContextoVaga | None) -> SecaoCurriculo: ...

class SugerirAjusteExperiencia:
    def __init__(self, ajustador_experiencia: AjustadorExperienciaPort,
                 melhorador: MelhoradorTextoCurriculoPort) -> None: ...
    def executar(self, experiencia: ExperienciaParaAvaliacao,
                 contexto: ContextoVaga | None) -> ExperienciaParaAvaliacao: ...
```

Regras dos casos de uso:

- `contexto` presente → porta de ajuste à vaga; ausente → `MelhoradorTextoCurriculoPort`.
- `SugerirAjusteExperiencia` devolve cargo, empresa e período do **input**, nunca os do provedor (RF5). O adapter atual já faz isso; o caso de uso reforça a regra.
- Seções aceitas: `PERFIL`, `TECNOLOGIAS`, `EXPERIENCIAS` (bloco de texto, fonte PDF). Outras → `ValueError` (RF3).
- Texto vazio já é barrado por `SecaoCurriculo`; experiência exige `descricao` não vazia (validator).
- Limite de 5.000 caracteres por texto enviado (validator), para conter custo e latência.
- `RuntimeError`/`ValueError` vindos da porta → `SugestaoIAIndisponivel` (mesmo padrão de `AvaliarExperiencia`).

Prompt do adapter `MelhoradorTextoCurriculoOpenAIClient`, seguindo o estilo de `AjustadorExperienciaOpenAIClient`:

- Reescrever com clareza, objetividade e verbos de ação.
- Manter o idioma do texto de entrada.
- Não inventar responsabilidades, tecnologias, resultados ou métricas.
- Preservar bullets iniciados por "-" (formato que o PDF reconhece).
- Resposta somente em JSON (`{"texto_sugerido": "..."}`).

Componente compartilhado (frontend):

```ts
interface SugestaoIAProps {
  rotuloBloco: string;                         // "resumo", "experiência 2"…
  obterTextoAtual: () => string;               // lê o campo no momento do clique (RF11)
  sugerir: (texto: string) => Promise<string>; // estratégia injetada pela tela
  aplicar: (sugestao: string) => void;         // setValue no campo do bloco (RF14)
}
```

Cada instância usa a própria `useMutation`. Isso isola o carregamento e o erro por bloco (RF15, RF16), e um novo pedido substitui a sugestão anterior.

### Modelos de Dados

Sem banco de dados. Contratos JSON:

```json
// POST /secoes-curriculo/sugestoes — requisição
{
  "secao": {"tipo": "PERFIL", "titulo": "Perfil", "conteudo": "texto atual"},
  "contexto_vaga": {                // opcional; ausente = modo "Meu perfil"
    "descricao_vaga": "...",
    "idioma_alvo": "en",
    "analise_vaga": {
      "requisitos": [{"nome": "Java", "categoria": "TECNOLOGIA", "tipo": "EXPLICITO", "origem": "DESCRICAO_VAGA"}],
      "ambiguidade": [],
      "texto_original": "..."
    }
  }
}
// resposta 200
{"conteudo_sugerido": "texto reescrito"}
```

```json
// POST /experiencias-profissionais/sugestoes — requisição
{"experiencia": {"cargo": "...", "empresa": "...", "periodo": "...", "descricao": "texto atual"},
 "contexto_vaga": { ... opcional ... }}
// resposta 200
{"descricao_sugerida": "texto reescrito"}
```

- `experiencia` reaproveita `ExperienciaParaAvaliacaoRequest` (já tem validação de descrição não vazia).
- `AnaliseVagaSchema` usa os nomes dos enums de `vaga/domain/analise_vaga.py` e fica em `schemas/vaga.py`, com `from_domain`/`to_domain`.
- Mudança no contrato da JOB-0033: `RascunhoAdaptadoResponse` ganha `analise_vaga: AnaliseVagaSchema`. Como a JOB-0033 ainda não está em produção, a mudança é aditiva e sem impacto.

### Endpoints de API

| Método e caminho | Descrição | Respostas |
|---|---|---|
| `POST /secoes-curriculo/sugestoes` | Sugestão para uma seção de texto | 200 (nada é persistido); 422 entrada inválida ou seção não aceita; 502 IA indisponível |
| `POST /experiencias-profissionais/sugestoes` | Sugestão para uma experiência; segue o padrão de `/experiencias-profissionais/avaliacoes` | 200; 422; 502 |

Os caminhos seguem `back-end-general-rules.md`: substantivos no plural; ação não-CRUD como sub-recurso; POST. Atualizar `job-sync.postman_collection.json`.

## Pontos de Integração

- **OpenAI**, via `ClienteOpenAI` (`shared_kernel/adapters/cliente_openai_client.py`). Sem credencial nova.
- **Erros:** falha ou resposta inválida do provedor → `SugestaoIAIndisponivel` → handler em `exceptions.py` → 502 com `ProblemaResponse` (`type_slug="sugestao-ia-indisponivel"`), igual aos handlers de avaliação.
- **Timeout:** o frontend usa o timeout de IA já existente (`ia: true` em `HttpApiClient`).

## Abordagem de Testes

TDD, conforme `.windsurf/rules/testing-rules.md`.

### Testes Unidade

Backend:

- `TestContextoVaga`: invariantes de descrição e idioma.
- `TestSugerirAjusteSecaoCurriculo`:
  - Com contexto, delega a `AjustadorTextoPort` com o texto **recebido**.
  - Sem contexto, delega a `MelhoradorTextoCurriculoPort`.
  - Rejeita `FORMACAO`, `CERTIFICACOES` e `IDIOMAS`.
  - Rejeita texto acima do limite.
  - Converte a falha da porta em `SugestaoIAIndisponivel`.
- `TestSugerirAjusteExperiencia`: as mesmas regras; preserva cargo, empresa e período mesmo se a porta (mock) devolver outros valores.
- `TestMelhoradorTextoCurriculoOpenAIClient`: monta o prompt com as regras; faz o parse do JSON; dispara erro com JSON inválido (mock de `ClienteOpenAI`, como em `test_ajustador_texto_client.py`).
- `TestAnaliseVagaSchema`: ida e volta `AnaliseVaga` ↔ JSON.
- Routers: 200, 422 e 502 nos dois endpoints; `analise_vaga` presente em `/rascunhos-adaptados`.

Frontend (Vitest):

- `SugestaoIA.test.tsx`:
  - Envia o texto atual do campo, não o inicial.
  - Mostra a sugestão sem alterar o campo.
  - Aplicar altera só o campo e marca dirty; Descartar não altera nada.
  - Erro mantém o texto e mostra a mensagem.
  - Fica desabilitado com campo vazio.
  - Anuncia a chegada via `aria-live`.
- `RevisaoCurriculoAdaptado.test.tsx`: botões presentes no resumo, nas tecnologias e em cada experiência; ausentes em formação, certificações e idiomas; o pedido leva `contexto_vaga`.
- `PerfilPage.test.tsx`: botões no resumo e nas experiências; o pedido vai sem `contexto_vaga`; aplicar não chama "salvar perfil".

### Testes de Serviço

- E2E (`frontend/e2e/fluxos.spec.ts`): pedir e aplicar uma sugestão na revisão, com API simulada.
- Acessibilidade (`acessibilidade.spec.ts`): estado com sugestão aberta.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. `ContextoVaga` e `AnaliseVagaSchema`. Sem dependências; destravam o resto.
2. `MelhoradorTextoCurriculoPort` e o adapter OpenAI.
3. `SugerirAjusteSecaoCurriculo` e `SugerirAjusteExperiencia`, com exceção e handler 502.
4. Endpoints, DI e Postman; `analise_vaga` na resposta do rascunho.
5. Cliente de API e tipos (`npm run gerar-tipos`).
6. Componente `SugestaoIA`.
7. Integração na revisão (exige a JOB-0033 entregue) e em "Meu perfil".
8. E2E e acessibilidade.

### Dependências Técnicas

- Bloqueante: entrega da JOB-0033 (tela de revisão, `shared/formulario-curriculo`, endpoint de rascunho).
- Os passos 1 a 4 e a integração em "Meu perfil" podem começar em paralelo à JOB-0033.

## Monitoramento e Observabilidade

- `INFO` em cada caso de uso: "Sugestão de IA gerada" com `modo` (`vaga`/`perfil`), `tipo` (seção ou experiência), tamanho do texto de entrada e de saída, e duração em ms.
- `WARNING` em falha do provedor, com o tipo da exceção (padrão de `AdaptarCurriculoParaVaga._avaliar_descricao_vaga`).
- Nunca logar conteúdo do texto, nome, e-mail ou descrição da vaga.
- As contagens permitem acompanhar a métrica do PRD (sugestões pedidas). As sugestões aplicadas só são observáveis no frontend; fora do escopo medir agora.

## Considerações Técnicas

### Decisões Principais

1. **Reusar as portas de ajuste existentes no modo vaga.** As sugestões ficam coerentes com a adaptação inicial, sem prompts duplicados. Alternativa rejeitada: um prompt novo para sugestões com vaga (duplicação).
2. **Porta nova para o modo sem vaga.** As portas atuais exigem `AnaliseVaga` e `descricao_vaga`. Passar valores vazios distorceria os prompts. Uma porta específica deixa a intenção explícita (ISP do SOLID).
3. **Um caso de uso por recurso, com a escolha de porta dentro dele.** São dois casos de uso em vez de quatro, e a regra "com ou sem vaga" fica em um só lugar. Um service não chama outro.
4. **`analise_vaga` vai e volta pelo frontend.** Evita uma chamada extra de IA (`JobDescriptionAnalyzerPort`) por sugestão. Trade-off: payload maior (alguns KB) e o servidor confia na análise enviada. O risco é baixo, porque a análise só orienta a reescrita do próprio usuário.
5. **Strategy no frontend.** `SugestaoIA` recebe `sugerir`; revisão e perfil injetam funções diferentes. Os componentes compartilhados não recebem flag de modo.
6. **Proposta antes de aplicar.** O texto só muda em "Aplicar", via `setValue`. Isso evita a corrida entre a resposta da IA e uma edição feita durante a espera.

### Riscos Conhecidos

- **Tecnologias inventadas no modo vaga:** a porta `AjustadorTextoPort` instrui a IA a incluir as tecnologias da vaga na seção de tecnologias (otimização ATS). Isso conflita com o RF6 do PRD. Mitigação proposta: o usuário vê a sugestão antes de aplicar. A decisão final está na questão em aberto 2 do PRD; se for "não incluir", criar um parâmetro na porta ou um prompt específico.
- **Custo de IA:** muitos cliques geram muitas chamadas. Mitigação: botão desabilitado durante o carregamento; limite de tamanho; logs com contagem para medir antes de decidir sobre limites.
- **Latência:** a mesma ordem de grandeza da avaliação de experiência. Mitigação: carregamento por bloco, sem travar a tela.
- **Qualidade do modo sem vaga:** é um prompt novo e sem histórico. Mitigação: testes com exemplos reais do projeto (`files_examples`) antes da entrega.

### Conformidade com Padrões

- `code-design-standards.md`: porta e Value Object em `curriculo/domain`, sem infraestrutura; adapter em `curriculo/adapters`; casos de uso em pacotes por funcionalidade com `executar` e injeção por construtor; nenhum service chama outro; schemas convertem para domínio/DTO.
- `back-end-general-rules.md`: recursos no plural, POST para ação não-CRUD, 200 sem persistência, 422 validação, 502 provedor indisponível; contratos existentes intactos (só um campo aditivo no rascunho da JOB-0033, ainda não publicada).
- `testing-rules.md`: `Test<Classe>`, AAA, sem comentários, mocks só para portas e `ClienteOpenAI`.
- `AGENTS.md`: DRY, Tell Don't Ask, SOLID (ISP na porta nova), hexagonal, Strategy, TDD.

### Arquivos relevantes e dependentes

- `src/jobsync/curriculo/domain/{ajustador_texto_port.py,ajustador_experiencia_port.py,curriculo.py,avaliacao_experiencia.py}`
- `src/jobsync/curriculo/adapters/{ajustador_texto_client.py,ajustador_experiencia_openai_client.py}` (referência de prompt e parse)
- `src/jobsync/curriculo/service_layer/avaliar_experiencia/` (referência de exceção e 502)
- `src/jobsync/vaga/domain/analise_vaga.py`
- `src/jobsync/shared_kernel/adapters/cliente_openai_client.py`
- `src/jobsync/entrypoints/api/{dependencies.py,exceptions.py,routers/curriculo_router.py,schemas/curriculo.py,schemas/vaga.py}`
- `src/jobsync/tests/curriculo/test_ajustador_texto_client.py` (padrão de teste de adapter)
- `frontend/src/shared/formulario-curriculo/*` (criados na JOB-0033)
- `frontend/src/features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx` (JOB-0033)
- `frontend/src/features/perfil/{PerfilPage.tsx,use-perfil-estruturado.ts}`
- `frontend/src/api/{api-client.ts,http-api-client.ts,tipos.ts,schema.d.ts}`
- `frontend/e2e/{fluxos.spec.ts,acessibilidade.spec.ts}`
- `job-sync.postman_collection.json`

## Questões em Aberto

1. Confirmar o limite de 5.000 caracteres por texto (valor proposto, não medido).
2. Definir o comportamento da sugestão de tecnologias no modo vaga (ver Riscos e PRD, questão 2).
3. Registrar no frontend quantas sugestões são aplicadas, para medir a utilidade? Exige um mecanismo de métricas que o projeto ainda não tem.

# Especificação Técnica — JOB-0045

PRD: `prd-job-0045.md` (mesma pasta).

## Resumo Executivo

Cada experiência passa a ter quatro blocos: contexto, responsabilidades, realizações e skills. Em `perfil_estruturado`, `ExperienciaProfissional` ganha `contexto`, `responsabilidades` e `skills`. As realizações reaproveitam o campo `conquistas` (banco da JOB-0042), que só muda de rótulo na UI. Em `curriculo`, `ExperienciaAdaptada` ganha `responsabilidades` e `skills`, e a IA devolve os quatro blocos em uma única chamada por experiência.

O reconhecimento dos blocos no texto é determinístico (parser de domínio, rótulos em português e inglês). A IA entra só para completar o que faltar e nunca reescreve o reconhecido. A migração de perfis antigos e a importação de PDF usam o mesmo domain service. O PDF mantém a convenção de texto, estendida com os quatro rótulos. A sincronia das skills com as tecnologias gerais é regra de domínio do agregado `PerfilEstruturado`.

Decisões fechadas com o produto: sem migration SQL (JSONB com leitura tolerante); formato do currículo adaptado sobe para a versão 2 e lê a versão 1; tecnologias gerais do perfil continuam uma lista plana; arrastar e soltar de tags nas competências do adaptado.

## Arquitetura do Sistema

### Visão Geral dos Componentes

**Novos**

| Componente | Camada | Responsabilidade |
|---|---|---|
| `shared_kernel/domain/rotulos_blocos_experiencia.py` | shared_kernel | Enum `BlocoExperiencia`, rótulos pt/en e apelidos reconhecidos (ex.: "Key Achievements", "Principais entregas") |
| `perfil_estruturado/domain/blocos_experiencia.py` | domain | VO `BlocosExperiencia` (parciais ou completos) e `ReconhecedorBlocosExperiencia` |
| `perfil_estruturado/domain/completador_blocos_experiencia_port.py` | domain (port) | Contrato para a IA completar só os blocos ausentes |
| `perfil_estruturado/domain/estruturar_experiencia_service.py` | domain service | Reconhece, chama a porta só para o que falta e junta (o reconhecido prevalece) |
| `perfil_estruturado/adapters/completador_blocos_experiencia_openai_client.py` | adapter | Implementa a porta via `ClienteOpenAI` |
| `perfil_estruturado/service_layer/migrar_experiencias_do_perfil/` | service | Migra experiências legadas e devolve rascunho, sem salvar (`service.py`, `dtos.py`, `validator.py`, `__init__.py`) |
| `frontend/src/shared/formulario-curriculo/EditorTags.tsx` | UI | Tags com criar, excluir e reordenar (dnd-kit), extraído do `EditorCompetencias` |

**Modificados**

- `perfil_estruturado/domain/perfil_estruturado.py`: novos campos, `eh_legada`, `para_texto(idioma)` e `com_tecnologias_das_experiencias()`.
- `perfil_estruturado/adapters/perfil_estruturado_repository_impl.py`: serialização e leitura tolerante.
- `perfil_estruturado/adapters/extrator_perfil_estruturado_client.py`: o prompt exige `descricao` literal, com os rótulos originais preservados.
- `perfil_estruturado/service_layer/importar_perfil_de_pdf/service.py`: chama `EstruturarExperiencia` por experiência.
- `perfil_estruturado/service_layer/salvar_perfil_estruturado/{dtos,service}.py`: novos campos, sincronia de skills e `tecnologias_incluidas` no output.
- `perfil_estruturado/domain/montar_curriculo_do_perfil_estruturado_service.py`: experiência em texto com os blocos, ou `descricao` se legada.
- `curriculo/domain/experiencia_adaptada.py`: `responsabilidades` e `skills`; `para_texto` e `para_avaliacao` com os quatro blocos.
- `curriculo/domain/rotulos_experiencia.py`: passa a derivar de `rotulos_blocos_experiencia`.
- `curriculo/domain/avaliacao_experiencia.py`: `ExperienciaParaAvaliacao` com `contexto`, `responsabilidades` e `skills`.
- `curriculo/domain/rascunho_curriculo_adaptado.py`: `ExperienciaEditada` com os quatro blocos e `para_curriculo` com os rótulos do idioma.
- `curriculo/adapters/ajustador_experiencia_openai_client.py`: prompt e parser dos quatro blocos; `refinar` também.
- `curriculo/adapters/pdf/interpretador_experiencias.py` e `estilo_curriculo_pdf.py`: leem e desenham os blocos.
- `curriculo/adapters/gerador_pdf_client.py`: ajustes de layout, se necessário.
- `curriculo/service_layer/{adaptar_curriculo_para_vaga,sugerir_ajuste_experiencia,sugerir_ajuste_experiencia_adaptada,avaliar_experiencia}`: DTOs e fluxo com os novos blocos.
- `curriculo_adaptado/adapters/serializador_conteudo.py`: versão 2.
- `entrypoints/api/curriculo_pre_montado.py`, `schemas/{curriculo,perfil_estruturado}.py` e `routers/perfil_estruturado_router.py`.
- `entrypoints/streamlit_app.py`: só o necessário para continuar funcionando.

**Frontend:** `formulario-perfil.ts`, `PerfilPage.tsx`, `ConquistasDaExperiencia.tsx`, `ImportarPerfilModal.tsx`, `RevisaoCurriculoAdaptado.tsx`, `formulario-revisao.ts`, `SugestaoExperienciaAdaptada.tsx`, `campos-curriculo.ts`, `EditorCompetencias.tsx`, `api/tipos.ts`, `api/schema.d.ts` e `api/http-api-client.ts`.

### Fluxo de dados

1. **Importação:** PDF → extrator (`descricao` literal) → `ImportarPerfilDePdf` chama `EstruturarExperiencia` por experiência → rascunho com os quatro blocos → revisão na tela → `SalvarPerfilEstruturado`.
2. **Migração:** perfil legado → `MigrarExperienciasDoPerfil` → rascunho → confirmação do usuário → `SalvarPerfilEstruturado`.
3. **Adaptação:** `curriculo_pre_montado` monta `ExperienciaParaAvaliacao` com os blocos → ajustador (1 chamada) → `ExperienciaAdaptada` → revisão → PDF.

## Design de Implementação

### Interfaces Principais

```python
# perfil_estruturado/domain/completador_blocos_experiencia_port.py
class CompletadorBlocosExperienciaPort(ABC):
    @abstractmethod
    def completar(self, experiencia: ExperienciaParaCompletar, idioma: str) -> BlocosExperiencia:
        """Gera só os blocos ausentes de `experiencia.reconhecidos`; devolve os quatro."""

# perfil_estruturado/domain/estruturar_experiencia_service.py
class EstruturarExperienciaService:
    def executar(self, experiencia: ExperienciaProfissional, idioma: str) -> ExperienciaProfissional: ...

# perfil_estruturado/domain/perfil_estruturado.py (PerfilEstruturado)
def tecnologias_ausentes(self) -> tuple[str, ...]: ...
def com_tecnologias_das_experiencias(self) -> PerfilEstruturado: ...
```

### Modelos de Dados

**`ExperienciaProfissional`** (frozen dataclass):

- campos novos: `contexto: str = ""`, `responsabilidades: tuple[str, ...] = ()`, `skills: tuple[str, ...] = ()`;
- invariantes: sem item vazio; sem skill duplicada (`normalizar_texto`); as `conquistas` seguem sem duplicata;
- `eh_legada`: tem `descricao` e nenhum dos quatro blocos;
- limites de 3 a 5 itens valem na geração pela IA e não são invariante: o usuário edita livremente.

**`ExperienciaAdaptada`:** adiciona `responsabilidades: tuple[str, ...] = ()` e `skills: tuple[str, ...] = ()`. `tem_conteudo` considera os quatro blocos.

**JSONB do perfil** (`experiencias_json`): chaves novas `contexto`, `responsabilidades` e `skills`, lidas com `.get(chave, padrão)`. `conquistas` continua com esse nome. Nenhuma migration SQL.

**JSON do currículo adaptado:** `VERSAO_DO_FORMATO = 2`. O leitor aceita as versões 1 e 2, e a versão 1 vem com blocos novos vazios. Versão desconhecida continua rejeitada.

**Convenção de texto do PDF** (idioma inglês; em português os rótulos são traduzidos):

```
Cargo — Empresa (Período)
Context: ...
Key Responsibilities:
- ...
Key Achievements:
- ...
Technologies: Java | PostgreSQL | ...
```

`InterpretadorExperiencias` passa a tratar o rótulo como cabeçalho de bloco. Os bullets seguintes pertencem ao bloco aberto. A linha `Technologies:` usa `|` como separador. O texto antigo (bullets sem rótulo e `Context:`) continua legível: bullets sem cabeçalho viram realizações.

**Drag and drop (UI):** o `EditorCompetencias` usa `@dnd-kit/core` e `@dnd-kit/sortable`, que o projeto já tem na tela de candidaturas. Cada categoria é um contêiner. As tags reordenam dentro da categoria e se movem entre categorias. O teclado funciona com `sortableKeyboardCoordinates`, e cada movimento é anunciado em `role="status"`. O estado continua controlado (`valor` e `aoMudar`). A regra de movimento (sem duplicar tag na categoria destino; categoria que esvazia é descartada ao salvar) fica em `competencias.ts`, testável sem DOM.

### Endpoints de API

Os contratos existentes ganham campos opcionais com padrão vazio, sem quebrar clientes:

- `POST/PUT /perfil-estruturado`: experiências com `contexto`, `responsabilidades`, `conquistas` e `skills`. A resposta do `PUT` traz `tecnologias_incluidas: string[]`.
- `POST /perfil-estruturado/importacoes`: devolve as experiências já com os quatro blocos.
- `POST /perfil-estruturado/{perfil_identificador}/migracoes-de-experiencias` (**novo**): devolve o perfil migrado como rascunho, sem persistir. `404` se o perfil não existe. Substantivo no plural, como pede a regra de recursos.
- Adaptação, sugestões por experiência, avaliação e geração de PDF revisado: o schema de experiência ganha `responsabilidades`, `skills` e `contexto`.

## Pontos de Integração

- OpenAI via `ClienteOpenAI` (já configurado), nos adapters `CompletadorBlocosExperienciaOpenAIClient` e `AjustadorExperienciaOpenAIClient`.
- Erro da IA na importação ou migração: a experiência volta com os blocos reconhecidos e os demais vazios, com um aviso. O usuário não perde o que o parser reconheceu.
- Erro da IA na adaptação: segue o tratamento atual (`SugestaoIAIndisponivel`).
- As chamadas à IA por experiência na importação e na migração rodam em paralelo (`ThreadPoolExecutor`, máximo de 4), para manter o tempo dentro do aviso atual de até 1 minuto.

## Abordagem de Testes

TDD, em `src/jobsync/tests/`, com nomes `TestNomeDaClasse` e sem comentários (`testing-rules.md`).

### Testes Unidade

- `ReconhecedorBlocosExperiencia`: rótulos em pt e en, apelidos, texto sem rótulo, bullets antes do primeiro rótulo, blocos parciais.
- `EstruturarExperienciaService` com porta fake: a IA é chamada só para blocos ausentes, o reconhecido prevalece, e há fallback quando a IA falha.
- `ExperienciaProfissional` e `PerfilEstruturado`: invariantes, `eh_legada`, `tecnologias_ausentes` e `com_tecnologias_das_experiencias` (maiúsculas, espaços, sem duplicar, não remove).
- `ExperienciaAdaptada`, `RascunhoCurriculoAdaptado` e `serializador_conteudo`: ida e volta na versão 2, leitura da versão 1, versão desconhecida rejeitada.
- `InterpretadorExperiencias` e `estilo_curriculo_pdf`: blocos, rótulos traduzidos e bloco vazio sem rótulo solto.
- Clientes OpenAI com `ClienteOpenAI` mockado: formato de resposta inválido e limites de 3 a 5 itens.
- `SalvarPerfilEstruturado` e `MigrarExperienciasDoPerfil` com repositório fake.
- Frontend (Vitest): `competencias.ts` (mover e reordenar tags), `formulario-perfil`, `formulario-revisao` e `EditorTags`, incluindo o teclado. O mock de `@dnd-kit/core` segue o padrão de `CandidaturasPage.test.tsx`.

### Testes de Serviço

- `test_perfil_estruturado_repository_impl`: ida e volta com os novos campos e leitura de JSON antigo sem eles.
- Routers: contratos de importação, salvamento (com `tecnologias_incluidas`), migração e adaptação.
- Playwright (`frontend/e2e`): importar um currículo com blocos, editar skills e arrastar uma tag. Requer ajuste em `e2e/apoio.ts`.
- Verificação manual com o exemplo da Starian: os blocos reconhecidos saem idênticos no PDF.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Rótulos em `shared_kernel` e refatoração de `rotulos_experiencia` (base de tudo, sem mudar comportamento).
2. Domínio do perfil: campos, invariantes e sincronia de skills.
3. Persistência (JSONB tolerante) e `SalvarPerfilEstruturado` com `tecnologias_incluidas`.
4. `ReconhecedorBlocosExperiencia`, porta, cliente e `EstruturarExperiencia`.
5. Importação e `MigrarExperienciasDoPerfil` com o endpoint.
6. `ExperienciaAdaptada`, serializador versão 2 e ajustador com os quatro blocos.
7. Interpretador e estilo do PDF; `MontarCurriculoDoPerfilEstruturado`.
8. API de adaptação, sugestões e avaliação.
9. Frontend: `EditorTags` com dnd-kit, perfil e revisão do adaptado.
10. E2E e verificação manual.

### Dependências Técnicas

- JOB-0009, JOB-0035, JOB-0041, JOB-0042 e JOB-0043 já integradas na branch.
- `@dnd-kit/*` já instalado.
- Sem infraestrutura nova.

## Monitoramento e Observabilidade

- INFO: `Experiencias estruturadas (total=%d, reconhecidas=%d, completadas_pela_ia=%d)` e `Tecnologias incluidas pelas skills (quantidade=%d)`.
- WARNING: falha da IA ao completar blocos (sem o texto do currículo).
- Texto de conquistas, contexto e skills nunca vai para o log (dado pessoal), só contagens.

## Considerações Técnicas

### Decisões Principais

- **Reaproveitar `conquistas` como realizações:** evita duplicar o banco da JOB-0042 e dispensa migração. Rejeitada a renomeação para `realizacoes`, porque quebraria o JSON salvo e os contratos sem ganho para o usuário.
- **Parser determinístico antes da IA:** garante o PRD (reconhecido nunca é reescrito) e reduz custo. Rejeitado "só LLM", por não garantir fidelidade.
- **Domain service compartilhado** entre importação e migração, porque um Service não pode usar outro Service (`code-design-standards.md`). A porta de IA fica em `perfil_estruturado`, sem um domínio importar o outro.
- **Convenção de texto no PDF**, em vez de estrutura no gerador: cobre também o PDF direto e reaproveita o interpretador. Trade-off: a IA pode não seguir a convenção, e então o PDF mostra a linha comum.
- **Tecnologias gerais em lista plana** no perfil. Categorias só no adaptado, onde a skill nova entra em "Tecnologias" e o usuário organiza arrastando.
- **Uma chamada de IA** com quatro blocos na adaptação, para não aumentar o tempo.

### Riscos Conhecidos

- **Métricas inventadas:** a regra do PRD permite estimar. Mitigação: aviso na revisão e prompts que preferem os dados da fonte.
- **Tempo da importação** com muitas experiências: paralelismo limitado a 4 e fallback sem IA.
- **Parser com rótulos inesperados:** apelidos configuráveis em `shared_kernel`, com casos de teste a cada novo apelido.
- **Perfis legados na adaptação direta:** seguem pela `descricao`, sem os novos blocos, até a migração.
- **Drag and drop acessível:** exige testes de teclado e anúncio de movimento.

### Conformidade com Padrões

- `.windsurf/rules/code-design-standards.md`: camadas hexagonais, porta no domínio e cliente em `adapters`, um Service não usa outro, DTOs e Validator por caso de uso, e nenhum domínio importa o `domain` de outro (os rótulos ficam em `shared_kernel`).
- `.windsurf/rules/back-end-general-rules.md`: recurso em substantivo plural (`migracoes-de-experiencias`), contratos existentes só ganham campos opcionais, e erros no formato padrão.
- `.windsurf/rules/testing-rules.md`: `TestClasse`, sem comentários, Arrange, Act e Assert separados, mocks só de `unittest.mock` e de serviços externos.
- `.windsurf/rules/general-rules.md` e `AGENTS.md`: TDD, mudanças só no necessário e imports conferidos pelo pacote real.
- Desvios: nenhum.

### Arquivos relevantes e dependentes

- Perfil: `perfil_estruturado/domain/{perfil_estruturado,montar_curriculo_do_perfil_estruturado_service,extrator_perfil_estruturado_port}.py`, `adapters/{perfil_estruturado_repository_impl,perfil_estruturado_repository_fake,extrator_perfil_estruturado_client}.py`, `service_layer/{importar_perfil_de_pdf,salvar_perfil_estruturado,adicionar_conquista_a_experiencia,verificar_conquistas_parecidas}`.
- Currículo: `curriculo/domain/{experiencia_adaptada,rascunho_curriculo_adaptado,avaliacao_experiencia,rotulos_experiencia,ajustador_experiencia_port,competencias}.py`, `adapters/{ajustador_experiencia_openai_client,gerador_pdf_client,avaliador_experiencia_jev_client,pdf/interpretador_experiencias,pdf/estilo_curriculo_pdf}.py`, `service_layer/{adaptar_curriculo_para_vaga,sugerir_ajuste_experiencia,sugerir_ajuste_experiencia_adaptada,avaliar_experiencia,gerar_pdf_curriculo_revisado,identificar_lacunas_da_vaga}`.
- `curriculo_adaptado/adapters/serializador_conteudo.py` e `curriculo_adaptado/domain/curriculo_adaptado.py`.
- `entrypoints/api/{curriculo_pre_montado,dependencies}.py`, `schemas/{curriculo,perfil_estruturado}.py`, `routers/{perfil_estruturado_router,curriculo_router}.py` e `entrypoints/streamlit_app.py`.
- `vaga_externa/service_layer/candidatar_na_vaga_externa/service.py` e `token_captura/domain/token_captura.py` (consumidores de experiência).
- Testes existentes que devem continuar verdes: `tests/curriculo/*`, `tests/perfil_estruturado/*`, `tests/curriculo_adaptado/*` e `tests/entrypoints/api/*`.
- Frontend: arquivos listados em Modificados, mais `PerfilPage.test.tsx`, `RevisaoCurriculoAdaptado.test.tsx`, `test/fixtures.ts` e `e2e/apoio.ts`.

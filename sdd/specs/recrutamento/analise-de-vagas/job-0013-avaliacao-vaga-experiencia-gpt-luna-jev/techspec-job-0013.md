# Tech Spec — Avaliação de vaga e experiência com Jev e GPT Luna 6 (JOB-0013)

- **Código**: `JOB-0013`
- **Módulo**: `recrutamento`
- **Subsistema**: `analise-de-vagas`
- **Status**: Rascunho
- **Baseado em**: [prd-job-0013.md](prd-job-0013.md)

## Resumo Executivo

A solução adiciona avaliações não persistidas via Jev e expõe os novos fluxos somente pela API FastAPI existente. Descrições de vagas poderão ser avaliadas isoladamente e também no fluxo de adaptação. Experiências poderão ser avaliadas sob demanda; após adaptação, cada item será avaliado separadamente quando a origem for um perfil estruturado. A resposta automática será incorporada de forma aditiva à resposta atual de adaptação.

O acesso aos modelos será isolado nos adapters: Jev usa o SDK oficial `typesafe-sdk` e GPT Luna 6 usa o SDK `openai` pela Responses API. Todos os usos atuais de `ClienteGroq` serão migrados para GPT Luna 6, inclusive extração, análise de requisitos, sugestões ATS e geração de carta. A análise de requisitos existente continua distinta da nova validação Jev.

## Arquitetura do Sistema

### Visão Geral dos Componentes

| Componente | Mudança e responsabilidade |
|---|---|
| `shared_kernel/adapters/cliente_openai_client.py` | Novo cliente OpenAI centralizado, configurado com `OPENAI_API_KEY` e `OPENAI_MODEL=gpt-6-luna`; mantém a operação JSON que os adapters atuais consomem. |
| `shared_kernel/adapters/cliente_jev_client.py` | Novo wrapper de `TypeSafeClient`, configurado com `TYPESAFE_API_KEY` e modelo Jev fixado por configuração. |
| `vaga/domain/` e `vaga/service_layer/avaliar_descricao_vaga/` | Novo resultado de avaliação, porta e caso de uso para completude, clareza, relevância e linguagem inclusiva. |
| `vaga/adapters/` | Novo adapter Jev que converte respostas tipadas em resultados do domínio, sem gerar explicações livres. |
| `curriculo/domain/` e `curriculo/service_layer/avaliar_experiencia/` | Nova porta, resultado e caso de uso para avaliar uma experiência em relação à descrição da vaga. |
| `curriculo/adapters/` | Novo adapter Jev para avaliar experiências profissionais. |
| `AdaptarCurriculoParaVaga` e seus DTOs | Executa a avaliação de vaga antes da adaptação; preserva os limites das experiências de perfil estruturado, adapta cada item e avalia os textos resultantes. |
| `MontarCurriculoDoPerfilEstruturado` | Fornece ao fluxo de adaptação as experiências estruturadas individuais, sem depender de segmentação heurística da seção agregada. |
| Adapters atuais de IA | `AjustadorTextoClient`, `ExtratorCurriculoClient`, `JobDescriptionAnalyzerClient`, `GerarCartaApresentacaoClient`, `GerarSugestoesAtsClient` e `ExtratorPerfilEstruturadoClient` passam a usar o cliente OpenAI. |
| Routers e schemas da API | `vaga_router.py` e `curriculo_router.py` recebem os endpoints e schemas de avaliação; a resposta de adaptação ganha campos opcionais para avaliações automáticas. |
| `api/dependencies.py`, `streamlit_app.py`, `requirements.txt`, `.env.example` | Atualizam composição, dependências e configuração dos clientes. A UI Streamlit não recebe novos fluxos. |

As avaliações são calculadas sob demanda e não são persistidas. Os casos de uso dependem das portas de avaliação; adapters de infraestrutura traduzem as primitivas e probabilidades do Jev para resultados de domínio. O GPT Luna 6 permanece responsável por geração e extração de texto.

## Design de Implementação

### Interfaces Principais

```python
class AvaliadorDescricaoVagaPort(ABC):
    @abstractmethod
    def avaliar(self, descricao_vaga: str) -> AvaliacaoDescricaoVaga: ...


class AvaliadorExperienciaPort(ABC):
    @abstractmethod
    def avaliar(
        self, experiencia: ExperienciaParaAvaliacao, descricao_vaga: str
    ) -> AvaliacaoExperiencia: ...
```

`AdaptarCurriculoParaVaga` recebe o avaliador de vaga e o avaliador de experiência por injeção. Para perfis estruturados, o DTO de entrada também carrega os itens de experiência individualmente; a aplicação adapta cada descrição preservando cargo, empresa e período, remonta a seção para gerar o PDF e avalia cada texto adaptado. Para entrada somente em PDF, a avaliação da descrição continua automática, mas a avaliação individual automática das experiências não é executada.

### Modelos de Dados

- `AvaliacaoDescricaoVaga`: score geral de 0 a 100 e resultados por dimensão: `completude`, `clareza`, `relevancia` e `inclusao`.
- `AvaliacaoExperiencia`: score geral de 0 a 100 e resultados por dimensão: `clareza_escrita`, `qualidade_detalhe`, `aderencia_vaga` e `consistencia_textual`.
- `ExperienciaParaAvaliacao`: estrutura de entrada com cargo, empresa, período e texto da experiência; não referencia diretamente a entidade de outro domínio.
- Cada dimensão contém score normalizado e nível/categoria de um catálogo fixo. Não há campo de explicação gerada pelo Jev.
- Para cada pergunta, o adapter usa a primitiva `Score` com cinco níveis ordinais (`0` a `4`) e descrições próprias da dimensão. Normaliza cada resultado por `score / 4 * 100`; o score geral é a média aritmética das dimensões, arredondada para inteiro. Pontuação maior representa melhor qualidade; a dimensão de inclusão mede linguagem mais inclusiva e a de consistência mede afirmações sustentadas pelo texto fornecido, sem verificação externa.
- As respostas HTTP usam schemas Pydantic separados dos modelos de domínio, com exemplos e descrições nos campos.

### Endpoints de API

| Método e caminho | Descrição |
|---|---|
| `POST /v1/vagas/avaliacoes` | Avalia uma descrição de vaga sob demanda. Recebe o texto e retorna score e categorias por dimensão. |
| `POST /v1/experiencias-profissionais/avaliacoes` | Avalia uma experiência enviada no corpo junto com a descrição da vaga-alvo. |
| `POST /v1/curriculos/{id}/adaptacoes` | Mantém o caminho existente; executa Jev antes da adaptação e acrescenta `avaliacao_vaga` e `status_avaliacao_vaga` à resposta. Para perfil estruturado, também retorna uma avaliação e status por experiência adaptada. |

O terceiro endpoint mantém o status e os campos atuais, acrescentando somente campos de resposta opcionais. As avaliações sob demanda são operações não persistidas. Os routers devem declarar `response_model`, `summary`, `description`, exemplos e respostas de erro conforme os padrões existentes.

## Pontos de Integração

- **OpenAI**: adicionar o pacote `openai`; usar `OpenAI.responses.create` com `model="gpt-6-luna"`. A variável `OPENAI_MODEL` permite configurar o identificador sem alterar código. Remover a dependência `groq` e substituir `GROQ_API_KEY` por `OPENAI_API_KEY` após migração de todos os consumidores.
- **TypeSafe AI**: adicionar `typesafe-sdk`; usar `TypeSafeClient` com o modelo `jev-1.14.0` (versão estável documentada no momento da especificação), via `TYPESAFE_API_KEY`. Cada dimensão é uma pergunta `Score`; dimensões do mesmo estado devem ser enviadas na mesma chamada para aproveitar a avaliação estruturada paralela.
- **Tratamento de falhas**: traduzir erros de autenticação, timeout, limite de cota e respostas inválidas em exceções de aplicação; usar o exception handler central da API e nunca expor chaves, payloads ou stack traces.
- **Privacidade**: não persistir entradas ou respostas da avaliação. Logs não devem conter texto de currículo ou descrição de vaga.
- **Indisponibilidade do Jev**: endpoints de avaliação sob demanda retornam erro de gateway conforme o handler central. Na adaptação, a falha de uma avaliação não bloqueia a geração do currículo; o resultado informa quais avaliações estão indisponíveis e retorna as avaliações concluídas.

## Abordagem de Testes

### Testes Unidade

- Testar clientes OpenAI e Jev com fakes dos SDKs, sem chamadas reais: configuração do modelo, transformação da resposta, resposta malformada, falha de autenticação e timeout.
- Testar normalização 0–100, média agregada, mapeamento de dimensões e níveis categóricos.
- Testar os serviços de avaliação com entradas vazias, diferentes dimensões, descrição de vaga contextual e falhas de adapter.
- Testar a adaptação com perfil estruturado para comprovar preservação de limites, avaliação individual de cada experiência e inclusão dos resultados; testar PDF para comprovar que não se tenta avaliar experiências individuais.
- Atualizar os testes dos adapters que migram de Groq para OpenAI, mantendo os contratos de saída existentes.

### Testes de Serviço e API

- Testar os dois endpoints sob demanda com `TestClient` e dependências substituídas, incluindo validação de schema e status de indisponibilidade do provedor.
- Testar o endpoint de adaptação com avaliadores fake: Jev é chamado antes do ajuste; nota baixa não interrompe a adaptação; perfis estruturados recebem uma avaliação por experiência.
- Não usar credenciais ou chamadas de modelo em testes automatizados. Seguir `testing-rules.md`: testar comportamento observável, separar Arrange/Act/Assert e não inserir comentários nos testes.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. Adicionar `ClienteOpenAI`, configuração e testes; migrar adapters Groq mantendo seus contratos.
2. Adicionar modelos de avaliação, ports e serviços para vaga e experiência.
3. Implementar `ClienteJev` e adapters de cada dimensão, com teste de contrato usando respostas fakes.
4. Preservar experiências individuais do perfil estruturado no DTO de adaptação e adaptar/avaliar cada item sem segmentar texto livre.
5. Adicionar schemas, endpoints, dependências e campos opcionais à resposta de adaptação.
6. Atualizar `.env.example`, dependências e instruções de configuração; executar testes unitários, de API e a suíte completa.

### Dependências Técnicas

- Acesso de API do Jev foi confirmado pelo usuário; configuração segura de `TYPESAFE_API_KEY` é necessária nos ambientes.
- Configurar `OPENAI_API_KEY` e validar uma chamada real de `gpt-6-luna` antes do deploy.
- Não há alteração de banco: os resultados das avaliações não são persistidos.

## Monitoramento e Observabilidade

- Registrar provedor/modelo, tipo de operação, duração, resultado e classe de erro; nunca registrar texto de vaga, currículo ou segredos.
- Contabilizar timeouts, respostas inválidas e falhas de autenticação separadamente para OpenAI e TypeSafe.
- Observar latência e uso de tokens da OpenAI, além da latência e confiança retornada pelo Jev, para detectar regressões de custo ou qualidade.

## Considerações Técnicas

### Decisões Principais

- **Separar geração e avaliação**: GPT Luna 6 substitui todos os usos de Groq; Jev só atende as novas avaliações. `JobDescriptionAnalyzerClient` continua extraindo requisitos para os fluxos atuais, mas passa a usar GPT Luna 6.
- **Não criar UI nesta entrega**: a funcionalidade fica exposta pela API FastAPI, conforme decisão do PRD.
- **Scores reproduzíveis**: níveis ordinais e categorias são definidos pelo produto; a aplicação normaliza e agrega scores, sem depender de explicações textuais do modelo.
- **Sem heurística de segmentação de PDF**: somente o perfil estruturado oferece experiências individuais após adaptação. Avaliação manual recebe um texto individual no corpo do endpoint.
- **Falha parcial na adaptação**: se Jev falhar antes da adaptação ou em uma avaliação de experiência, continuar o fluxo e sinalizar como indisponíveis somente as avaliações que falharam. Scores baixos também não bloqueiam a adaptação.
- **Clientes síncronos**: manter os serviços/adapters sincronizados com os fluxos existentes de Streamlit. As operações HTTP síncronas são executadas pelo thread pool do FastAPI, não bloqueando o event loop; documentar essa escolha contra a preferência por adapters assíncronos.

### Riscos Conhecidos

- Score e confiança não garantem que uma descrição seja justa nem que uma experiência seja verdadeira. O resultado é apoio à revisão, não decisão automatizada de contratação.
- A migração altera seis consumidores atuais de Groq e exige atualização coordenada das credenciais e testes. Mitigar com testes de contrato fakes e verificação manual de fluxos representativos.
- A avaliação automática de experiências depende de o fluxo de adaptação manter os itens estruturados separados até concluir a avaliação.
- Instruções e rubricas afetam a calibração. Validar os níveis com exemplos representativos em português e inglês antes de fixar limiares ou usar score para decisões futuras.
- Regras de retenção e processamento de dados dos provedores ainda precisam ser definidas.

### Questões em Aberto

1. Quais são os requisitos de retenção, uso e exclusão dos dados enviados aos provedores?

### Conformidade com Padrões

- Segue `code-design-standards.md`: portas nos domínios, use cases na camada de aplicação, adapters concretos na infraestrutura, DTOs para transporte e composição centralizada.
- Segue `back-end-general-rules.md`: endpoints REST versionados, schemas Pydantic, `response_model`, códigos HTTP apropriados e handler central.
- Segue `testing-rules.md` e `AGENTS.md`: testes pytest focados em comportamento observável e separação de camadas.
- Desvio documentado: clientes e services continuam síncronos para preservar os consumidores Streamlit e a arquitetura atual; o FastAPI executa operações síncronas em seu thread pool. Uma migração completa para APIs assíncronas fica fora desta mudança.

### Arquivos Relevantes e Dependentes

- `sdd/specs/recrutamento/analise-de-vagas/job-0013-avaliacao-vaga-experiencia-gpt-luna-jev/prd-job-0013.md`
- `src/jobsync/shared_kernel/adapters/cliente_groq_client.py` (substituído) e novo `cliente_openai_client.py`, `cliente_jev_client.py`
- `src/jobsync/vaga/domain/analise_vaga.py`, novo port e serviço de avaliação; `src/jobsync/vaga/adapters/job_description_analyzer_client.py`
- `src/jobsync/curriculo/domain/curriculo.py`, `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/`
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`, `extrator_curriculo_client.py`, `gerar_carta_apresentacao_client.py`, `gerar_sugestoes_ats_client.py`
- `src/jobsync/perfil_estruturado/domain/montar_curriculo_do_perfil_estruturado_service.py`, `src/jobsync/perfil_estruturado/adapters/extrator_perfil_estruturado_client.py`
- `src/jobsync/entrypoints/api/dependencies.py`, `src/jobsync/entrypoints/api/routers/vaga_router.py`, `curriculo_router.py`, `schemas/vaga.py`, `schemas/curriculo.py`, `main.py`
- `src/jobsync/tests/vaga/`, `src/jobsync/tests/curriculo/`, `src/jobsync/tests/perfil_estruturado/`
- `requirements.txt`, `.env.example`, `README.md`

### Referências Técnicas

- TypeSafe AI, Quickstart e SDK Python: https://docs.typesafe.ai/introduction/quickstart
- TypeSafe AI, primitivas `Score`: https://docs.typesafe.ai/primitives/score
- TypeSafe AI, modelos: https://docs.typesafe.ai/models
- OpenAI, GPT-6 Luna: https://developers.openai.com/api/docs/models/gpt-6-luna

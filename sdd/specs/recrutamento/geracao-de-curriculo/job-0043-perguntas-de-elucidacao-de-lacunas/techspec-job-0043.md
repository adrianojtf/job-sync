# Especificação Técnica — JOB-0043

## Resumo Executivo

A etapa de perguntas vira três casos de uso pequenos, cada um com seu endpoint, para não alterar o contrato do `POST` de adaptação:

1. **Identificar lacunas:** uma chamada de IA compara a vaga com o histórico do candidato (resumo, experiências, conquistas do banco) e devolve até 5 lacunas, cada uma com um tema e uma pergunta.
2. **Redigir conquista:** a partir do caso descrito pelo candidato, a IA escreve a conquista, sem acrescentar fato. O candidato revisa.
3. **Adicionar conquista à experiência:** comando no domínio do perfil que grava a conquista aprovada, com origem `RESPOSTA_PERGUNTA`, no banco da JOB-0042.

Depois disso, o fluxo de adaptação existente já enxerga as conquistas novas nas experiências (seleção da JOB-0042). Para o **resumo** usá-las, o `ContextoVaga` passa a carregar as conquistas do histórico, e o prompt do Perfil as recebe como base. Falha da IA em qualquer etapa nunca bloqueia a geração: a identificação de lacunas falha para "sem lacunas", como `_planejar` já faz para equivalências.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Novos, em `curriculo` (dono do resultado; recebe o histórico como dado, sem importar o domínio `perfil_estruturado`):

- `domain/lacuna_da_vaga.py`: `LacunaDaVaga` (VO: tema, pergunta) e `HistoricoDoCandidato` (VO: resumo, experiências com conquistas, tecnologias).
- `domain/identificador_lacunas_port.py`: `IdentificadorLacunasPort`.
- `domain/redator_conquista_port.py`: `RedatorConquistaPort`.
- `adapters/identificador_lacunas_openai_client.py` e `adapters/redator_conquista_openai_client.py`.
- `service_layer/identificar_lacunas_da_vaga/` e `service_layer/redigir_conquista_de_lacuna/`: `service.py`, `dtos.py`.

Novos, em `perfil_estruturado`:

- `service_layer/adicionar_conquista_a_experiencia/`: `AdicionarConquistaAExperiencia` (usa `PerfilEstruturadoRepository`).
- `PerfilEstruturado.com_conquista_na_experiencia(indice, conquista)`: método de domínio que devolve o perfil novo (Tell, Don't Ask).

Modificados:

- `curriculo/domain/contexto_vaga.py`: campo `conquistas_do_historico: tuple[str, ...] = ()`.
- `curriculo/adapters/ajustador_texto_client.py`: o prompt do Perfil inclui as conquistas do histórico como base de fatos.
- `entrypoints/api/routers/curriculo_router.py`: `POST /curriculo/lacunas` e `POST /curriculo/lacunas/conquista-rascunho`, e o preenchimento de `conquistas_do_historico` na adaptação.
- `entrypoints/api/routers/perfil_estruturado_router.py`: `POST /perfil-estruturado/experiencias/{indice}/conquistas`.
- `entrypoints/api/schemas/curriculo.py`, `schemas/perfil_estruturado.py`, `entrypoints/dependencies.py`: schemas e injeção.
- `frontend/src/features/ajustar-vaga/`: etapa "Perguntas sobre a vaga" e o hook.

## Design de Implementação

### Interfaces Principais

```python
@dataclass(frozen=True)
class LacunaDaVaga:
    tema: str
    pergunta: str

class IdentificadorLacunasPort(ABC):
    @abstractmethod
    def identificar(
        self, historico: HistoricoDoCandidato, contexto: ContextoVaga
    ) -> tuple[LacunaDaVaga, ...]: ...

class RedatorConquistaPort(ABC):
    @abstractmethod
    def redigir(
        self, lacuna: LacunaDaVaga, caso: str, cargo: str, idioma_alvo: str
    ) -> str: ...
```

Regras no domínio: `LacunaDaVaga` não aceita tema nem pergunta vazios; `principais(lacunas, limite=5)` remove duplicatas de tema e corta no limite. O limite de 5 não depende da IA obedecer ao prompt.

### Modelos de Dados

Sem migração. As conquistas aprovadas entram no JSONB do perfil (JOB-0042). As lacunas e as respostas não são persistidas: só a conquista aprovada vive no banco.

### Endpoints de API

- `POST /curriculo/lacunas`: entrada `{descricao_vaga, cargo_alvo, idioma_alvo}`. O router lê o perfil do usuário autenticado. Saída `{lacunas: [{tema, pergunta}]}`; lista vazia sem lacunas ou com falha da IA.
- `POST /curriculo/lacunas/conquista-rascunho`: entrada `{tema, pergunta, caso, experiencia_indice, idioma_alvo}`. Saída `{texto}`. Sem persistência.
- `POST /perfil-estruturado/experiencias/{indice}/conquistas`: entrada `{texto}`; grava com origem `RESPOSTA_PERGUNTA`. Saída: o perfil atualizado. Índice inexistente devolve 404, e texto vazio, 422.
- O aviso de duplicidade usa o endpoint da JOB-0042 (`/perfil-estruturado/conquistas/parecidas`) antes de adicionar.

## Pontos de Integração

Provedor de IA existente (`ClienteOpenAI`), com duas chamadas novas (lacunas e redação), ambas por `solicitar_json`.

- **Lacunas:** o prompt pede temas centrais da vaga e do cargo-alvo (práticas, tipo de atuação), exclui o que o histórico já sustenta, ordena por centralidade e devolve no máximo 5 perguntas fechadas ("Você já..."). Temas, e não só tecnologias, porque a `AnaliseVaga` atual só traz requisitos técnicos.
- **Redação:** só o que o candidato informou; sem número, resultado ou tecnologia que ele não citou; verbo de ação; idioma alvo.
- **Latência:** uma chamada extra antes da geração. A tela mostra o estado de carregamento e o botão "Pular perguntas e gerar" fica ativo desde o início. Medir na avaliação manual contra o limite de 1 minuto.
- **Resumo:** o `ContextoVaga` recebe os textos das conquistas do perfil, e a instrução do Perfil (JOB-0040) trata essas conquistas como fatos que o histórico sustenta.

## Abordagem de Testes

### Testes Unidade

- `LacunaDaVaga` e `principais`: vazio, duplicata de tema, corte em 5.
- `IdentificarLacunasDaVaga`: lista da porta limitada a 5; falha (`RuntimeError`/`ValueError`) vira tupla vazia com log; perfil sem experiências devolve vazio sem chamar a IA.
- Adapters: prompt de lacunas traz vaga, cargo-alvo e histórico; prompt de redação traz a proibição de acrescentar fato; resposta fora do formato levanta `ValueError`.
- `PerfilEstruturado.com_conquista_na_experiencia`: índice válido e inválido, origem e duplicata.
- `AdicionarConquistaAExperiencia`: persiste via repositório; perfil inexistente.
- `AjustadorTextoClient`: o prompt do Perfil inclui as conquistas do histórico; sem conquistas, o prompt não muda (regressão da JOB-0040).
- Routers: os três endpoints, incluindo 404 e 422 e a falha da IA devolvendo lista vazia.
- Frontend (vitest): sem lacunas a etapa não aparece; fluxo Sim, escolha da experiência, caso, revisão e aprovação; Não e Prefiro não responder; Pular.

### Avaliação manual

Perfil com lacunas e duas vagas (FDE e engenharia de software). Critérios: as perguntas cobrem os temas centrais ausentes e não repetem o que o perfil mostra; o resumo e as conquistas não citam tema não confirmado.

## Sequenciamento de Desenvolvimento

1. Domínio de lacunas, porta, adapter e `IdentificarLacunasDaVaga`.
2. Endpoint `POST /curriculo/lacunas`.
3. Redator de conquista e o endpoint de rascunho.
4. Comando de adicionar conquista e o endpoint (usa a JOB-0042).
5. Resumo usando as conquistas do histórico.
6. Frontend da etapa de perguntas.
7. Avaliação manual.

Dependências bloqueantes: JOB-0042 (banco e endpoint de parecidas) e JOB-0040 (regra do resumo).

## Monitoramento e Observabilidade

Logs informativos: número de lacunas identificadas e quantas foram respondidas "Sim"; aviso quando a identificação falha. Sem texto de vaga, perfil, caso ou conquista nos logs.

## Considerações Técnicas

### Decisões Principais

- **Endpoints próprios, e não embutir na adaptação.** O contrato atual não muda, e "Pular" segue igual. Alternativa rejeitada: um endpoint com duas fases.
- **Lacunas e respostas sem persistência.** Só a conquista aprovada é guardada (YAGNI). "Não" não é lembrado, e isso fica em aberto no PRD.
- **Falha da IA vira "sem lacunas".** Mesma política de `_planejar`: a geração nunca depende desta etapa.
- **Comando de adicionar conquista no perfil, e não `PUT` do perfil inteiro.** A tela de ajuste não carrega o formulário do perfil, e o comando evita sobrescrever edições concorrentes.
- **Conquistas do banco inteiro no contexto do resumo.** O pedido de adaptação não carrega "as respostas desta geração" (sem estado), e todas as conquistas do banco já foram aprovadas pelo usuário.
- **Domínio `curriculo` recebe `HistoricoDoCandidato`.** Respeita a regra de não importar o `model` de outro domínio; o router monta o VO a partir do perfil.

### Riscos Conhecidos

- A latência da etapa pode estourar o aviso de 1 minuto. Mitigação: chamada única, "Pular" sempre disponível e medição.
- As perguntas podem repetir o que o perfil já mostra. Mitigação: o prompt exclui o sustentado, o histórico inclui conquistas, e a avaliação manual confere.
- A resposta "Sim" pode ser falsa. A responsabilidade é do usuário: origem registrada e aviso de revisão mantido.
- O prompt do resumo pode crescer com muitas conquistas. Mitigação: limitar a N mais recentes se a avaliação indicar.

### Conformidade com Padrões

- `AGENTS.md`: TDD, DDD, hexagonal, mudança mínima.
- `.windsurf/rules/code-design-standards.md`: um Service por caso de uso com `executar`, sem Service chamando Service, DTOs no pacote, domínio sem infraestrutura, sem import de model entre domínios.
- `.windsurf/rules/testing-rules.md` e `back-end-general-rules.md`: a rever na execução das tasks.

### Arquivos relevantes e dependentes

- `src/jobsync/curriculo/domain/contexto_vaga.py`
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/service.py`
- `src/jobsync/perfil_estruturado/domain/perfil_estruturado.py`
- `src/jobsync/perfil_estruturado/domain/perfil_estruturado_repository.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/entrypoints/api/routers/perfil_estruturado_router.py`
- `frontend/src/features/ajustar-vaga/`
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0042-banco-de-conquistas-por-experiencia/`
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0040-resumo-aderente-a-vaga/`

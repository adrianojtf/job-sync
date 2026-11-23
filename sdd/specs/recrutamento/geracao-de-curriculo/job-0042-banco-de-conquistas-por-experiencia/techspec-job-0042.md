# Especificação Técnica — JOB-0042

## Resumo Executivo

O banco de conquistas entra como um novo Value Object `Conquista`, guardado **dentro de cada `ExperienciaProfissional`** do agregado `PerfilEstruturado`. As experiências já ficam em `perfil_estruturado.experiencias_json` (JSONB), então não há migração de schema: perfis antigos abrem com a lista vazia e o upsert atual de `PerfilEstruturadoRepositoryImpl.salvar` continua o único ponto de gravação.

Na adaptação, as conquistas da experiência chegam ao `AjustadorExperienciaOpenAIClient` junto com a descrição. A **mesma chamada** que hoje escreve "conquistas + contexto" passa a escolher de 3 a 5 conquistas do banco, as mais aderentes à vaga, e a reescrevê-las sem acrescentar fato. Não há chamada extra de IA. O aviso de duplicidade é uma regra de domínio determinística (texto normalizado e sobreposição de palavras), exposta por um endpoint sem estado.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Novos:

- `perfil_estruturado/domain/perfil_estruturado.py`: `OrigemConquista` (enum) e `Conquista` (VO).
- `perfil_estruturado/domain/conquistas_parecidas.py`: função pura de similaridade textual.
- `perfil_estruturado/service_layer/verificar_conquistas_parecidas/`: `service.py` (`VerificarConquistasParecidas`), `dtos.py`.
- `curriculo/adapters/prompt_contexto_vaga.py`: nova constante `REGRA_SELECAO_DE_CONQUISTAS`.

Modificados:

- `ExperienciaProfissional`: novo campo `conquistas: tuple[Conquista, ...] = ()` e o método `conquistas_parecidas_com(texto)`.
- `perfil_estruturado_repository_impl.py`: serialização e leitura de `conquistas` no JSONB, com `[]` quando ausente.
- `entrypoints/api/schemas/perfil_estruturado.py`: `ConquistaRequest/Response` e o campo `conquistas` (opcional, padrão vazio) nos schemas de experiência.
- `entrypoints/api/routers/perfil_estruturado_router.py`: `POST /perfil-estruturado/conquistas/parecidas`.
- `curriculo/domain/avaliacao_experiencia.py`: `ExperienciaParaAvaliacao.conquistas: tuple[str, ...] = ()`.
- `entrypoints/api/routers/curriculo_router.py`: `_experiencias_do_perfil` repassa os textos das conquistas.
- `curriculo/adapters/ajustador_experiencia_openai_client.py`: prompt com o bloco de conquistas cadastradas e a regra de seleção.
- `frontend/src/features/perfil/` (`PerfilPage.tsx`, `formulario-perfil.ts`, hook): lista de conquistas por experiência, com cadastro, edição, exclusão e aviso de duplicidade.

Fluxo: perfil salvo com conquistas, depois `POST /curriculo/...` lê o perfil, `_experiencias_do_perfil` monta as experiências com conquistas, `AdaptarCurriculoParaVaga._ajustar_experiencias` chama `AjustadorExperienciaPort.ajustar`, e o prompt faz a seleção.

## Design de Implementação

### Interfaces Principais

```python
class OrigemConquista(Enum):
    MANUAL = auto()
    RESPOSTA_PERGUNTA = auto()  # usada pela JOB-0043

@dataclass(frozen=True)
class Conquista:
    texto: str
    origem: OrigemConquista = OrigemConquista.MANUAL

# ExperienciaProfissional
def conquistas_parecidas_com(self, texto: str) -> tuple[Conquista, ...]: ...

# conquistas_parecidas.py
def sao_parecidas(texto_a: str, texto_b: str) -> bool: ...
```

`sao_parecidas` normaliza (minúsculas, sem acento, sem pontuação), ignora palavras curtas e compara a sobreposição de palavras com um limite nomeado (constante, inicialmente 0,6). Textos iguais após a normalização são sempre parecidos.

Porta da IA: sem nova porta. `AjustadorExperienciaPort.ajustar` já recebe `ExperienciaParaAvaliacao`, que ganha `conquistas`.

### Modelos de Dados

Sem migração. Cada item de `experiencias_json` passa a aceitar `"conquistas": [{"texto": "...", "origem": "MANUAL"}]`. A leitura usa `.get("conquistas", [])`, e a escrita serializa explicitamente cada experiência (o `__dict__` atual não serializa o `Conquista` aninhado). Invariantes: o texto da conquista não é vazio; conquistas iguais na mesma experiência são rejeitadas no domínio.

### Endpoints de API

- `PUT /perfil-estruturado` e `GET`: os payloads de experiência ganham `conquistas` (opcional, padrão `[]`). Contrato retrocompatível.
- `POST /perfil-estruturado/conquistas/parecidas`: entrada `{texto, conquistas: [texto]}`, saída `{parecidas: [texto]}`. Sem estado: o formulário edita em memória até salvar, então a comparação usa o que a tela tem, e não o que está persistido.

## Pontos de Integração

Provedor de IA existente (`ClienteOpenAI`), sem novo uso. A seleção reaproveita a chamada de `ajustar`.

Regras de prompt (`REGRA_SELECAO_DE_CONQUISTAS`), aplicadas quando há conquistas cadastradas:

- escolha de 3 a 5 conquistas, as mais aderentes à vaga e ao cargo-alvo, a mais relevante primeiro (esta faixa substitui a de 2 a 6 do prompt de sistema);
- reescrita permitida para adequar o vocabulário, sem acrescentar fato, número, resultado, tecnologia ou prática;
- com menos de 3 conquistas, usar todas e completar pela descrição, como hoje;
- não forçar relação com a vaga: se nenhuma se relaciona, escolher as 3 mais próximas.

Conflito a resolver na implementação: o prompt de sistema atual permite "propor métricas plausíveis" quando a descrição não tem número (JOB-0035). Para conquistas do banco a regra nova prevalece e deve estar no prompt do usuário, depois do bloco das conquistas. Sem conquistas cadastradas, nada muda. Experiência sem descrição mas com conquistas deixa de cair em `_sem_conteudo`.

## Abordagem de Testes

### Testes Unidade

Seguindo `testing-rules.md` (TDD, Arrange/Act/Assert, `unittest.mock` só para serviços externos):

- `Conquista` e `ExperienciaProfissional`: texto vazio, duplicata exata e `conquistas_parecidas_com` com paráfrase, caixa e acento.
- `sao_parecidas`: casos parecidos e distintos, e estabilidade do limite.
- Repositório (integração, fixture `pool_postgres` existente): salvar e ler com conquistas; ler linha antiga sem a chave `conquistas`.
- Schemas e routers: payload com e sem `conquistas`; endpoint de parecidas.
- `_experiencias_do_perfil`: repassa os textos das conquistas.
- Ajustador: o prompt traz as conquistas, a regra de 3 a 5, a proibição de acrescentar número e o fallback para a descrição; experiência sem conquistas mantém o prompt atual (regressão); experiência com conquistas e sem descrição chama a IA.
- Frontend (vitest): lista, cadastro, edição, exclusão e aviso de duplicidade em `PerfilPage`.

Limite conhecido: testes com cliente falso confirmam o prompt, não a qualidade da escolha.

### Avaliação manual

Mesmo perfil com 6 ou mais conquistas por experiência, adaptado a duas vagas de áreas diferentes. Critérios: as conquistas escolhidas mudam conforme a vaga, estão entre 3 e 5, e não trazem fato ou número ausente do banco.

## Sequenciamento de Desenvolvimento

1. Domínio (`Conquista`, similaridade, `ExperienciaProfissional`) e persistência: base de tudo.
2. API do perfil: schemas e endpoint de parecidas.
3. Seleção na adaptação: `ExperienciaParaAvaliacao`, router, prompt do ajustador.
4. Frontend do banco no perfil.
5. Avaliação manual e ajuste dos limites.

Dependências bloqueantes: nenhuma externa. A JOB-0043 depende desta.

## Monitoramento e Observabilidade

Em `AdaptarCurriculoParaVaga`, um log informativo com o número de experiências que tinham banco e o total de conquistas enviadas. Sem textos de conquista no log (dado pessoal).

## Considerações Técnicas

### Decisões Principais

- **JSONB dentro da experiência, e não tabela própria.** Sem migração, perfis antigos intactos e um único salvar. Trade-off: não se consulta conquista fora do perfil, o que o PRD não exige. Alternativa rejeitada: tabela `conquista` (migração 0004 e novo repositório sem demanda atual).
- **Seleção na mesma chamada.** Não adiciona latência. Alternativa rejeitada: ranqueamento separado, com uma chamada por experiência.
- **Duplicidade por texto, no domínio.** Determinístico e testável. Pode deixar passar paráfrases, e o aviso é só informativo.
- **Endpoint de parecidas sem estado.** Evita acoplar o aviso ao estado salvo.
- **`ExperienciaParaAvaliacao` com o campo novo.** Dívida de nome: o VO também serve à adaptação. Aceita por KISS; renomear fica fora do escopo.

### Riscos Conhecidos

- O banco grande pode pesar no prompt. Mitigação: medir na avaliação manual e, se preciso, limitar o envio às N conquistas mais recentes (decisão registrada na task final).
- A IA pode acrescentar número ao reescrever. Mitigação: a regra explícita, o teste de prompt e o aviso de revisão existente.
- O limite de similaridade pode gerar falsos positivos. Mitigação: o aviso não bloqueia; constante nomeada e testada.

### Conformidade com Padrões

- `AGENTS.md`: mudança mínima, TDD, DDD, hexagonal, DRY.
- `.windsurf/rules/code-design-standards.md`: VO no domínio sem infraestrutura, Service com `executar`, DTO no pacote do Service, sem dependência entre Services, UI converte entidades em DTO.
- `.windsurf/rules/testing-rules.md` e `back-end-general-rules.md`: a rever na execução das tasks.

### Arquivos relevantes e dependentes

- `src/jobsync/perfil_estruturado/domain/perfil_estruturado.py`
- `src/jobsync/perfil_estruturado/adapters/perfil_estruturado_repository_impl.py`
- `src/jobsync/entrypoints/api/schemas/perfil_estruturado.py`
- `src/jobsync/entrypoints/api/routers/perfil_estruturado_router.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/curriculo/domain/avaliacao_experiencia.py`
- `src/jobsync/curriculo/adapters/ajustador_experiencia_openai_client.py`
- `src/jobsync/curriculo/adapters/prompt_contexto_vaga.py`
- `frontend/src/features/perfil/`
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0035-conquistas-e-contexto-nas-experiencias/`

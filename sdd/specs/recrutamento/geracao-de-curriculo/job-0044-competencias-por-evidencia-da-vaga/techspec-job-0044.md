# Especificação Técnica — JOB-0044

## Resumo Executivo

A decisão do que entra em Competências sai do prompt e vai para o domínio. Um serviço de domínio puro, `SelecaoDeCompetencias`, recebe os itens que o candidato tem, o texto das suas experiências, os requisitos da vaga e as equivalências da JOB-0037, e devolve o **conjunto permitido** e as **lacunas**. A IA só agrupa em categorias e ordena os itens permitidos. Depois dela, o domínio descarta qualquer item fora do conjunto e aplica o teto de 45.

Também saem a frase "todas as tecnologias da análise de vaga devem aparecer" de `_solicitar` (vale para todas as seções) e o título "Tecnologias": o catálogo passa a "Competências" (pt) e "Skills" (en).

## Arquitetura do Sistema

### Visão Geral dos Componentes

Novos, em `curriculo/domain`:

- `selecao_de_competencias.py`: `SelecaoDeCompetencias` (serviço de domínio puro), `ResultadoDaSelecao` (itens permitidos e lacunas) e a função `limitar_ao_teto`.

Modificados:

- `curriculo/adapters/ajustador_texto_client.py`: remove a frase obrigatória de `_solicitar`; a instrução de `TECNOLOGIAS` lista os itens permitidos, pede ordenar pela relevância à vaga e proíbe item fora da lista. `ajustar_secao` recebe o conjunto permitido (parâmetro opcional).
- `curriculo/domain/ajustador_texto_port.py`: assinatura de `ajustar_secao` ganha `itens_permitidos`.
- `curriculo/service_layer/adaptar_curriculo_para_vaga/service.py`: calcula a seleção antes da IA, filtra a saída da IA e preenche as lacunas no rascunho.
- `curriculo/domain/rascunho_curriculo_adaptado.py`: campo `lacunas_tecnologia: tuple[str, ...]`, informativo como `ajustes_tecnologia`.
- `shared_kernel/domain/catalogo_localizacao.py`: `tecnologias` passa a `{"pt": "Competências", "en": "Skills"}`.
- `entrypoints/api/schemas/curriculo.py`: `lacunas_tecnologia` em `RascunhoCurriculoAdaptadoSchema` (só na resposta; ignorado na entrada).
- `frontend`: título "Competências" em `RevisaoCurriculoAdaptado.tsx` e `formulario-revisao.ts`; aviso das lacunas ao lado de `AjusteTecnologiaLista`; `api/schema.d.ts` regenerado.

Fluxo: `AdaptarCurriculoParaVaga` -> `SelecaoDeCompetencias` (permitidos e lacunas) -> `AjustadorTextoClient` (agrupa e ordena) -> filtro de domínio (fora do conjunto, teto) -> `competencias` do rascunho.

## Design de Implementação

### Interfaces Principais

```python
@dataclass(frozen=True)
class ResultadoDaSelecao:
    permitidos: tuple[str, ...]
    lacunas: tuple[str, ...]

class SelecaoDeCompetencias:
    def selecionar(
        self,
        itens_do_candidato: Sequence[str],
        textos_das_experiencias: Sequence[str],
        requisitos_da_vaga: Sequence[RequisitoTecnico],
        equivalencias: Sequence[EquivalenciaTecnologia],
    ) -> ResultadoDaSelecao: ...

def limitar_ao_teto(
    categorias: Sequence[CategoriaCompetencia], relevantes: Container[str], teto: int = 45
) -> tuple[CategoriaCompetencia, ...]: ...
```

Regras de `selecionar`:

1. Considera da vaga só requisitos com categoria `TECNOLOGIA` ou `FERRAMENTA`. Os demais (habilidade, metodologia, outra) nunca entram nem viram lacuna.
2. Permitidos = itens do candidato, mais os requisitos da vaga que `menciona_tecnologia` encontra nos textos das experiências, mais o `alvo` de cada equivalência aplicada. Comparação sem diferenciar maiúsculas e minúsculas, sem duplicatas, na ordem do candidato.
3. Lacunas = requisitos considerados que não estão nos permitidos, na ordem de aparição na vaga.

`limitar_ao_teto` remove, a partir do fim, primeiro os itens que não estão em `relevantes` (os que a vaga pede), e só depois os relevantes, até chegar ao teto. Categorias que ficam sem item são descartadas.

### Modelos de Dados

Sem mudança de banco. `RascunhoCurriculoAdaptado.lacunas_tecnologia` não é persistido em `curriculo_adaptado` (a lista vale para a geração em curso). O serializador de conteúdo (JOB-0041) não muda.

### Endpoints de API

Sem endpoints novos. `RascunhoAdaptadoResponse.rascunho` ganha `lacunas_tecnologia`.

## Pontos de Integração

- Entrada de itens do candidato: para o perfil estruturado, `perfil.tecnologias`; para PDF, os itens lidos da seção de tecnologias do PDF (`categorias_de_texto`). Nos dois casos o `Curriculo` de partida já traz a seção `TECNOLOGIAS` em texto, que o serviço converte em itens.
- Textos das experiências: `ExperienciaParaAvaliacao.descricao` (perfil) ou o texto da seção de experiências (PDF).
- JOB-0043 consome `lacunas_tecnologia`. Esta entrega não cria endpoint nem tela de perguntas.
- Falha da IA de agrupamento: mantém o comportamento atual (erro de geração). Falha na seleção não ocorre (domínio puro).

## Abordagem de Testes

### Testes Unidade

Pytest, TDD, regras de `testing-rules.md`:

- `SelecaoDeCompetencias`: perfil puro; vaga com tecnologia sem evidência vira lacuna; tecnologia citada só em experiência entra; equivalência entra; requisito de habilidade ou metodologia é ignorado; maiúsculas e minúsculas; duplicatas; ordem.
- `limitar_ao_teto`: abaixo do teto não muda; acima do teto remove primeiro os não relevantes e depois os relevantes; categoria vazia some; ordem preservada.
- `ajustador_texto_client`: o prompt de `TECNOLOGIAS` traz a lista permitida e a proibição; nenhum prompt traz a frase "todas as tecnologias"; os demais prompts não mudam.
- `AdaptarCurriculoParaVaga` com fakes: item acrescentado pela IA é descartado; teto aplicado; lacunas no rascunho; seção ausente não gera lacunas indevidas.
- Catálogo e PDF: título "Competências" em pt e "Skills" em en.
- Schema e router: `lacunas_tecnologia` na resposta e ignorado na entrada.
- Frontend (Vitest): título "Competências", aviso de lacunas com e sem itens, e testes existentes ajustados ao novo título.

Limite conhecido: testes com IA falsa confirmam o contrato, não a qualidade do agrupamento. Avaliação manual com a vaga de agentes de IA e um perfil real, com chaves reais (a cargo do autor).

## Sequenciamento de Desenvolvimento

1. `SelecaoDeCompetencias` e `limitar_ao_teto` (domínio puro, sem I/O).
2. Prompt: remover a frase obrigatória; instrução de `TECNOLOGIAS` com a lista permitida.
3. Integração no serviço de adaptação e `lacunas_tecnologia` no rascunho e na API.
4. Título "Competências"/"Skills" no catálogo, na tela e nos testes.
5. Aviso de lacunas na revisão.
6. E2E e avaliação manual.

## Monitoramento e Observabilidade

Log `info` com as contagens: itens do candidato, permitidos, lacunas, itens descartados da saída da IA e itens cortados pelo teto. Sem listar os itens.

## Considerações Técnicas

### Decisões Principais

- **O domínio decide, a IA arruma.** Prompt sozinho pediria à IA que respeite uma regra de veracidade; o filtro posterior garante o resultado. Alternativa rejeitada: só endurecer o prompt, que não dá garantia e não se testa.
- **Evidência por busca de texto**, com `menciona_tecnologia` (já usada pelo `PlanoAdaptacao`). Simples e testável. Não reconhece sinônimos; ver Riscos.
- **Só `TECNOLOGIA` e `FERRAMENTA` entram ou viram lacuna.** Depende da classificação da análise da vaga.
- **Título em inglês "Skills"**, por ser o mais seguro nas recomendações pesquisadas (PRD, Questões em Aberto 1).
- **`lacunas_tecnologia` fora do banco.** Evita acoplar o objeto salvo (JOB-0041) à geração; a JOB-0043 pode persistir o que precisar.

### Riscos Conhecidos

- Sinônimos ("Postgres" e "PostgreSQL") viram lacuna falsa. Mitigação: o aviso é só informativo, e o editor permite adicionar a tag. Lista de sinônimos fica para depois.
- A análise da vaga pode classificar um conceito como tecnologia. Mitigação: o conceito vira lacuna, nunca entra na lista. Medir na avaliação manual.
- Mudar a assinatura de `AjustadorTextoPort` quebra os fakes de teste existentes; atualizar na mesma tarefa.
- Perfis com poucos itens e vagas muito diferentes geram lista curta. Aceito: é o comportamento desejado.

### Conformidade com Padrões

- `AGENTS.md`: DDD, domínio puro e imutável, TDD, KISS (sem lista de sinônimos), mudança mínima.
- `.windsurf/rules/testing-rules.md`: testes. `code-design-standards.md` e `back-end-general-rules.md`: revisar no início das tasks.

### Arquivos relevantes e dependentes

- `src/jobsync/curriculo/domain/plano_adaptacao.py` e `equivalencia_tecnologia.py` (`menciona_tecnologia`)
- `src/jobsync/curriculo/domain/competencias.py` (JOB-0041)
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/service.py`
- `src/jobsync/shared_kernel/domain/catalogo_localizacao.py`
- `src/jobsync/entrypoints/api/schemas/curriculo.py`
- `frontend/src/features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx`, `formulario-revisao.ts`
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0043-perguntas-de-elucidacao-de-lacunas/` (branch `claude/sharp-bohr-q9898q`)

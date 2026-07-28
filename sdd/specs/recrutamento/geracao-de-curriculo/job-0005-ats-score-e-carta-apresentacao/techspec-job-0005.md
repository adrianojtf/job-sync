# Especificação Técnica

## Resumo Executivo

Esta Tech Spec descreve a implementação do ATS Score e da geração de carta de apresentação, conforme `prd-job-0005.md`. Ambas as funcionalidades são implementadas como novos use cases que consomem os mesmos objetos já produzidos pelo fluxo existente (`AnaliseVaga` e o `Curriculo` adaptado retornado por `AdaptarCurriculoParaVaga`), sem exigir nova extração ou nova chamada de análise de vaga. O cálculo do ATS Score é lógica pura de domínio/aplicação (sem IA); a carta de apresentação usa o mesmo adapter Groq já existente (`AjustadorTextoGroq`), através de uma nova porta dedicada.

## Arquitetura do Sistema

### Visão Geral dos Componentes

- `CalcularAtsScore` (novo use case, `application/use_cases/calcular_ats_score.py`): recebe `Curriculo` adaptado + `AnaliseVaga`, retorna `ResultadoAtsScore` (nota + requisitos faltantes). Lógica pura, sem porta externa.
- `ResultadoAtsScore` (novo, `domain/ats_score.py`): value object com `nota: int` (0-100) e `requisitos_faltantes: tuple[RequisitoTecnico, ...]`.
- `GeradorCartaApresentacaoPort` (novo, `application/ports/gerador_carta_apresentacao_port.py`): interface para gerar texto de carta a partir do currículo adaptado e da análise de vaga.
- `GeradorCartaApresentacaoGroq` (novo, `infrastructure/llm/gerador_carta_apresentacao_groq.py`): implementação usando o `ClienteGroq` já existente (mesmo cliente usado por `AjustadorTextoGroq`).
- `GerarCartaApresentacao` (novo use case, `application/use_cases/gerar_carta_apresentacao.py`): orquestra a chamada à porta acima.
- `AdaptarCurriculoParaVaga` (existente, `application/use_cases/adaptar_curriculo_para_vaga.py`): **não é modificado** — o `ResultadoAdaptacao` que ele já retorna (`curriculo_adaptado`) é suficiente como entrada para os dois novos use cases, orquestrados a partir da UI, não de dentro do use case existente. Isso evita acoplar o caso de uso principal a funcionalidades opcionais.
- `ui/app_streamlit.py` (modificado): após chamar `AdaptarCurriculoParaVaga`, chama em sequência `CalcularAtsScore` e `GerarCartaApresentacao`, exibindo os três resultados (PDF, score, carta) na mesma tela.

Fluxo de dados proposto:
1. UI chama `AdaptarCurriculoParaVaga.executar()` (fluxo atual, sem mudanças) → obtém `ResultadoAdaptacao` (contém `curriculo_adaptado` e implicitamente a `AnaliseVaga` usada).
2. UI chama `CalcularAtsScore.executar(curriculo_adaptado, analise_vaga)` → `ResultadoAtsScore`.
3. UI chama `GerarCartaApresentacao.executar(curriculo_adaptado, analise_vaga, idioma_alvo)` → texto da carta.
4. UI renderiza PDF (existente) + nota/lacunas + botão de download da carta.

Nota de integração: `ResultadoAdaptacao` hoje não expõe a `AnaliseVaga` usada internamente — será necessário adicionar o campo `analise_vaga: AnaliseVaga` a esse dataclass para reaproveitá-la sem recalcular (ver "Pontos de Integração").

## Design de Implementação

### Interfaces Principais

```python
class GeradorCartaApresentacaoPort(ABC):
    @abstractmethod
    def gerar(
        self,
        curriculo: Curriculo,
        analise_vaga: AnaliseVaga,
        idioma_alvo: str,
    ) -> str:
        """Retorna o texto da carta de apresentação."""
        ...
```

`CalcularAtsScore` não precisa de porta — é função pura:

```python
class CalcularAtsScore:
    def executar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga) -> ResultadoAtsScore:
        ...
```

### Modelos de Dados

```python
@dataclass(frozen=True)
class ResultadoAtsScore:
    nota: int  # 0-100
    requisitos_faltantes: tuple[RequisitoTecnico, ...]
```

Regra de cálculo (lógica pura, sem IA):
- Considerar apenas `RequisitoTecnico` com `tipo == TipoRequisitoTecnico.EXPLICITO`.
- Um requisito é "coberto" se seu `nome` (case-insensitive, normalizado) aparece em algum `conteudo` de `SecaoCurriculo` do currículo adaptado.
- `nota = round(100 * cobertos / total_explicitos)`; se `total_explicitos == 0`, `nota = 100` (nenhum requisito explícito para cobrir).

### Endpoints de API

Não aplicável — mesmo modelo monolítico Streamlit do restante do projeto.

## Pontos de Integração

- `application/use_cases/adaptar_curriculo_para_vaga.py`: adicionar campo `analise_vaga: AnaliseVaga` ao dataclass `ResultadoAdaptacao` (linha 38-43), preenchido com o valor já calculado na linha 65 do método `executar`. Mudança aditiva, não quebra os testes existentes que constroem `ResultadoAdaptacao` — checar `tests/application/test_adaptar_curriculo_para_vaga.py` para ajustar construções do dataclass nos testes afetados.
- `infrastructure/llm/cliente_groq.py`: reaproveitado sem alteração pelo novo `GeradorCartaApresentacaoGroq`.
- `infrastructure/llm/ajustador_texto_groq.py`: usado como referência de padrão de prompt (não é chamado diretamente pela carta).

## Abordagem de Testes

### Testes Unidade

- `CalcularAtsScore`: casos cobrindo cobertura total (100), cobertura parcial, zero requisitos explícitos (nota 100), e case-insensitivity na comparação de nomes.
- `GerarCartaApresentacao`: usando um fake de `GeradorCartaApresentacaoPort` (mesmo padrão de `tests/application/test_adaptar_curriculo_para_vaga.py`), validando que idioma e análise de vaga são repassados corretamente à porta.
- `GeradorCartaApresentacaoGroq`: seguindo o padrão de `tests/infrastructure/llm/test_ajustador_texto_groq.py`, validando que o prompt inclui a análise de vaga estruturada e não apenas o texto bruto.

### Testes de Integração

- Fluxo end-to-end (mockando a chamada Groq) validando que `ResultadoAdaptacao.analise_vaga` chega corretamente aos dois novos use cases sem recalcular a análise.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. `ResultadoAtsScore` (domain) + `CalcularAtsScore` (application), com testes unitários — não depende de nada novo, pode ser feito primeiro e isoladamente.
2. Adicionar `analise_vaga` a `ResultadoAdaptacao` e ajustar testes existentes afetados.
3. `GeradorCartaApresentacaoPort` + `GeradorCartaApresentacaoGroq` + `GerarCartaApresentacao`, com testes.
4. Integração na UI: exibir score, lacunas e botão de download da carta na tela de resultado.
5. Validação manual com uma vaga real, conferindo que a nota bate com a lista de requisitos explícitos exibida.

### Dependências Técnicas

- Nenhuma biblioteca nova — reaproveita `groq` já presente em `requirements.txt`.
- Depende da Fase 0 (`job-0004`) apenas se o histórico de notas por perfil for desejado no futuro; para esta fase, ATS Score e carta funcionam de forma stateless, sem exigir login.

## Monitoramento e Observabilidade

- Logar (nível INFO) a nota calculada e a quantidade de requisitos faltantes por execução, sem logar o conteúdo do currículo.
- Logar (nível ERROR) falhas na chamada Groq para geração de carta, com fallback de mensagem amigável na UI ("não foi possível gerar a carta agora, tente novamente").

## Considerações Técnicas

### Decisões Principais

- ATS Score como lógica pura (sem IA): mais previsível, testável e sem custo de API adicional — a extração de requisitos já usa IA (`JobDescriptionAnalyzerGroq`), então a comparação final não precisa.
- Carta de apresentação via IA (não template estático): a vaga e o currículo variam demais para um template genérico produzir algo útil; o padrão de prompt estruturado já validado em `AjustadorTextoGroq` é reaproveitado.
- Orquestração na UI, não dentro de `AdaptarCurriculoParaVaga`: mantém o caso de uso principal focado em uma responsabilidade (gerar o PDF adaptado), evitando que ele cresça para conhecer funcionalidades opcionais.

### Riscos Conhecidos

- A nota de ATS Score pode divergir da percepção do usuário se o currículo usar sinônimos não reconhecidos pela comparação textual simples (ex.: "JS" vs "JavaScript") — mitigação: normalizar termos comuns na comparação, mas sem tentar ser um matcher semântico completo nesta fase.
- Geração de carta depende de disponibilidade da API Groq — mesma limitação já documentada no README do projeto para o fluxo de adaptação.

### Conformidade com Padrões

Não há regras em `.windsurf/rules` no repositório (diretório inexistente) — nenhum desvio a documentar. Segue a Arquitetura Hexagonal existente: `ResultadoAtsScore` no domínio, portas em `application/ports`, adapter Groq em `infrastructure/llm`.

### Arquivos relevantes e dependentes

- `sdd/specs/recrutamento/geracao-de-curriculo/job-0005-ats-score-e-carta-apresentacao/prd-job-0005.md`
- `domain/ats_score.py` (novo)
- `application/use_cases/calcular_ats_score.py` (novo)
- `application/ports/gerador_carta_apresentacao_port.py` (novo)
- `application/use_cases/gerar_carta_apresentacao.py` (novo)
- `infrastructure/llm/gerador_carta_apresentacao_groq.py` (novo)
- `application/use_cases/adaptar_curriculo_para_vaga.py` (modificado — campo `analise_vaga` em `ResultadoAdaptacao`)
- `tests/application/test_adaptar_curriculo_para_vaga.py` (modificado)
- `ui/app_streamlit.py` (modificado)

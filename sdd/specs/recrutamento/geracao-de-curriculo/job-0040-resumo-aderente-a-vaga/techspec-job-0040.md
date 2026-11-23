# Especificação Técnica — JOB-0040

## Resumo Executivo

A mudança é só de instrução à IA. A seção Perfil é reescrita por `AjustadorTextoClient` com a instrução `_INSTRUCOES_POR_TIPO[TipoSecao.PERFIL]`, que hoje pede para "enfatizar a experiência e competências mais alinhadas à vaga". Essa instrução será trocada por uma regra do resumo: cobrir os temas da vaga e o senso comum do cargo, em frases próprias, curtas e sem inventar fatos.

A regra fica em uma constante em `prompt_contexto_vaga.py`, ao lado de `REGRA_RESPONSABILIDADES_IMPLICITAS` (JOB-0037), e é reutilizada pelo refino do resumo (foco `ADERENCIA_VAGA`). Não há mudança de API, banco, domínio nem frontend.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Modificados:

- `src/jobsync/curriculo/adapters/prompt_contexto_vaga.py`: nova constante `REGRA_RESUMO_ADERENTE_A_VAGA`.
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`: `_INSTRUCOES_POR_TIPO[PERFIL]` passa a usar a nova regra; `_instrucao_da_secao` mantém o complemento de tecnologia equivalente já existente para o Perfil.
- `src/jobsync/curriculo/adapters/prompt_refino.py`: o foco `ADERENCIA_VAGA` aponta para a mesma regra quando a seção é o Perfil (ver Decisões).
- `src/jobsync/tests/curriculo/test_ajustador_texto_client.py`: novos testes de prompt.

Não modificados: `ContextoVaga` (já traz `cargo_alvo`, `descricao_vaga` e `analise_vaga`), `AdaptarCurriculoParaVaga`, routers e schemas.

Fluxo: `AdaptarCurriculoParaVaga` -> `AjustadorTextoClient.ajustar_secao(PERFIL)` -> prompt com a regra -> resumo. O refino segue `refinar_secao` -> `bloco_refino`.

## Design de Implementação

### Interfaces Principais

Sem novas interfaces. `AjustadorTextoPort` não muda.

```python
REGRA_RESUMO_ADERENTE_A_VAGA = (
    "Reescreva o resumo profissional em até 3 frases. Mostre os temas centrais da vaga e o que é "
    "comum ao cargo-alvo, mesmo quando a vaga não os detalha, apenas se o histórico do candidato "
    "os sustentar. Escreva com frases próprias e não copie trechos da vaga. Mantenha-se fiel aos "
    "fatos originais: não invente anos de experiência ou cargos, nem métricas."
)
```

O texto acima é a redação implementada na task 1.0; "tecnologias" ficou fora da lista de proibições para não conflitar com as tecnologias equivalentes (JOB-0037). A redação final será ajustada contra o conjunto de vagas de teste.

### Modelos de Dados

Nenhuma mudança.

### Endpoints de API

Nenhuma mudança.

## Pontos de Integração

Provedor de IA existente (`ClienteOpenAI`), sem novo uso. O prompt de sistema `_PROMPT_SISTEMA` já pede cargo-alvo para a ênfase e proíbe inventar fatos; fica como está.

## Abordagem de Testes

### Testes Unidade

Seguindo `testing-rules.md` (TDD, Arrange/Act/Assert, sem comentários, `unittest.mock`) e o padrão dos testes de `test_ajustador_texto_client.py`, que já verificam o conteúdo do prompt enviado:

- O prompt do Perfil contém a regra (limite de frases, "não copie", "não invente").
- O prompt do Perfil continua trazendo o cargo-alvo quando informado e o complemento de tecnologia equivalente.
- O prompt das outras seções não recebe a regra do resumo (teste existente de isolamento por tipo).
- `refinar_secao` do Perfil com foco de aderência inclui a regra, e as outras seções não.

Limite conhecido: testes com cliente falso confirmam o prompt, não a qualidade do texto gerado.

### Avaliação manual

Conjunto de vagas de teste (engenharia de software, Forward Deployed Engineer, cargo fora de TI) com perfil real. Critérios: temas cobertos, sem cópia, sem fato inventado, até o limite de tamanho. Resultado registrado na task de fechamento.

## Sequenciamento de Desenvolvimento

1. Teste vermelho do prompt do Perfil, depois a constante e o uso em `ajustador_texto_client.py`.
2. Reuso no refino (`prompt_refino.py`) com teste.
3. Avaliação manual e ajuste da redação.

Sem dependências bloqueantes.

## Monitoramento e Observabilidade

Sem novos logs. O log de adaptação existente do serviço basta.

## Considerações Técnicas

### Decisões Principais

- **Só prompt, sem verificador em tempo de execução.** Mantém KISS/YAGNI e não adiciona chamada à IA. Alternativa rejeitada: validar cópia por n-gramas e regerar. Custa latência e só se justifica se a avaliação manual mostrar cópia recorrente.
- **Regra genérica, sem lista de cargos.** Mesma decisão da JOB-0037: o modelo usa o senso comum do cargo-alvo.
- **Reuso no refino do Perfil.** Evita que "Sugestões de IA" desfaça a regra. A forma exata (parâmetro de `bloco_refino` ou regra por seção) será decidida no TDD; a primeira opção é passar o tipo da seção a `bloco_refino`.

### Riscos Conhecidos

- A IA pode afirmar práticas que o histórico não cobre. Mitigação: condição explícita "apenas se o histórico sustentar", aviso de revisão existente e avaliação manual.
- O limite de 3 frases pode cortar conteúdo útil em perfis longos. Mitigação: ajustar após a avaliação.

### Conformidade com Padrões

- `AGENTS.md`: mudança mínima, TDD, reuso das constantes de prompt existentes, DRY.
- `.windsurf/rules/testing-rules.md`: nomenclatura e estrutura dos testes.
- `.windsurf/rules/code-design-standards.md` e `back-end-general-rules.md`: a revisar na execução das tasks (não lidos nesta fase).

### Arquivos relevantes e dependentes

- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/adapters/prompt_contexto_vaga.py`
- `src/jobsync/curriculo/adapters/prompt_refino.py`
- `src/jobsync/curriculo/domain/contexto_vaga.py`
- `src/jobsync/tests/curriculo/test_ajustador_texto_client.py`
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0037-aderencia-de-experiencias-e-resumo-a-vaga/`

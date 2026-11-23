# Especificação Técnica — JOB-0040

## Resumo Executivo

A mudança é só de instrução à IA. A seção Perfil é reescrita por `AjustadorTextoClient` com a instrução `_INSTRUCOES_POR_TIPO[TipoSecao.PERFIL]`, que hoje pede para "enfatizar a experiência e competências mais alinhadas à vaga". Essa instrução será trocada por uma regra do resumo: cobrir os temas da vaga e o senso comum do cargo, em frases próprias, curtas e sem inventar fatos.

A regra fica em uma constante em `prompt_contexto_vaga.py`, ao lado de `REGRA_RESPONSABILIDADES_IMPLICITAS` (JOB-0037), e é reutilizada pelo refino do resumo (foco `ADERENCIA_VAGA`). Não há mudança de API, banco, domínio nem frontend.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Modificados:

- `src/jobsync/curriculo/adapters/prompt_contexto_vaga.py`: nova constante `REGRA_RESUMO_ADERENTE_A_VAGA`.
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`: `_INSTRUCOES_POR_TIPO[PERFIL]` passa a usar a nova regra; `_instrucao_da_secao` mantém o complemento de tecnologia equivalente já existente para o Perfil.
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
2. Testes de caracterização do refino do Perfil (sem mudança de código).
3. Avaliação manual e ajuste da redação.

Sem dependências bloqueantes.

## Monitoramento e Observabilidade

Sem novos logs. O log de adaptação existente do serviço basta.

## Considerações Técnicas

### Decisões Principais

- **Só prompt, sem verificador em tempo de execução.** Mantém KISS/YAGNI e não adiciona chamada à IA. Alternativa rejeitada: validar cópia por n-gramas e regerar. Custa latência e só se justifica se a avaliação manual mostrar cópia recorrente.
- **Regra genérica, sem lista de cargos.** Mesma decisão da JOB-0037: o modelo usa o senso comum do cargo-alvo.
- **Refino do Perfil sem mudança de código.** `_solicitar` inclui a instrução da seção em todo pedido, inclusive em `refinar_secao`. A regra do resumo já chega ao refino em qualquer foco (aderência, impacto, palavras-chave, clareza), e o limite de 3 frases e a proibição de copiar a vaga valem para todos. `prompt_refino.py` não muda; testes de caracterização fixam o comportamento (task 2.0).

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

## Atualização após a avaliação manual

A avaliação com a vaga Forward Deployed Engineer Sênior reprovou a primeira redação da regra (PRD, "Resultado da primeira avaliação manual"). A task 3.0 ajusta a constante `REGRA_RESUMO_ADERENTE_A_VAGA` para:

- limite de 60 palavras, em um parágrafo de até 3 frases (o limite de frases sozinho foi contornado com frases longas);
- proibição de listas de termos, ponto e vírgula e referências à vaga ou à oportunidade;
- no máximo 3 temas da vaga, escritos como ações do candidato;
- o cargo-alvo como eixo, sem declarar como título um cargo que o candidato não exerceu;
- omissão de tema sem sustentação no histórico.

Risco novo: o foco "palavras-chave" do refino (`_FOCOS` em `prompt_refino.py`) pede "os termos exatos da vaga" e pode conflitar com "não copie trechos da vaga" no resumo. A task 3.0 fixa isso com teste e, se preciso, restringe o foco no Perfil.

Se a nova avaliação ainda mostrar cópia ou excesso de tamanho, reabrir a decisão "só prompt" e avaliar um verificador de tamanho e sobreposição (alternativa já registrada em "Decisões Principais").

Causa adicional (task 3.0): `_solicitar` incluía em todas as seções a ordem "inclua todas as tecnologias da análise de vaga, mesmo que não estejam no conteúdo original". No Perfil isso induzia a lista de termos. O Perfil agora recebe uma instrução oposta (`_instrucao_de_tecnologias_da_vaga`); as outras seções não mudam.

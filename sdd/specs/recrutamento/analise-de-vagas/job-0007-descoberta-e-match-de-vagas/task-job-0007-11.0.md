# Tarefa 11.0: Implementar filtro por período em DescobrirVagasComMatch

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Estender `DescobrirVagasComMatch.executar` com o parâmetro `dias_maximo`, repassando-o a cada buscador e aplicando um filtro adicional (client-side) sobre a lista deduplicada, antes do corte por `LIMITE_VAGAS_ANALISADAS` e da análise por IA.

<requirements>
- `DescobrirVagasComMatch.executar(self, termo: str, pdf_curriculo: bytes, dias_maximo: int | None = None) -> tuple[VagaComScore, ...]`.
- `dias_maximo` é repassado a cada `buscador.buscar(termo, dias_maximo)` na busca paralela.
- Após deduplicar, se `dias_maximo is not None`: mantém vagas onde `data_publicacao is None` (data desconhecida — sempre mantida, decisão de produto) OU `(hoje - data_publicacao).days <= dias_maximo`.
- O filtro por período acontece ANTES do corte por `LIMITE_VAGAS_ANALISADAS`, para não desperdiçar chamadas de IA analisando vagas fora da janela pedida.
- Quando `dias_maximo is None` (comportamento padrão), nenhum filtro de data é aplicado — comportamento idêntico ao atual.
- Complexidade: medium.
</requirements>

## Subtarefas

- [ ] 11.1 Atualizar a assinatura de `DescobrirVagasComMatch.executar` com o parâmetro `dias_maximo`.
- [ ] 11.2 Repassar `dias_maximo` para cada `buscador.buscar(...)` na busca paralela.
- [ ] 11.3 Implementar o filtro por `data_publicacao` sobre a lista deduplicada, antes do corte por `LIMITE_VAGAS_ANALISADAS`.
- [ ] 11.4 Testes cobrindo: vaga dentro da janela mantida, vaga fora da janela removida, vaga com `data_publicacao=None` sempre mantida mesmo com filtro ativo, e comportamento inalterado quando `dias_maximo=None`.

## Detalhes de Implementação

Consultar a seção "Fluxo de dados proposto" (passo 4.1, atualizado) de `techspec-job-0007.md`.

## Critérios de Sucesso

- Com `dias_maximo` informado, apenas vagas dentro da janela (ou com data desconhecida) chegam à etapa de análise por IA.
- Sem `dias_maximo`, o comportamento é idêntico ao já existente (nenhuma regressão).

## Testes da Tarefa

- [ ] Teste unitário: vaga com `data_publicacao` dentro da janela pedida é mantida.
- [ ] Teste unitário: vaga com `data_publicacao` fora da janela pedida é removida.
- [ ] Teste unitário: vaga com `data_publicacao=None` é mantida mesmo com `dias_maximo` ativo.
- [ ] Teste unitário: sem `dias_maximo`, nenhuma vaga é removida por data.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/application/use_cases/descobrir_vagas_com_match/use_case.py`
- `src/tests/application/use_cases/descobrir_vagas_com_match/test_use_case.py`

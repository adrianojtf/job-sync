# Tarefa 1.0: ContextoVaga e AnaliseVagaSchema

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar o Value Object que agrupa o contexto da vaga e o schema que serializa `AnaliseVaga` nos dois sentidos, para o frontend reenviar a análise sem nova chamada de IA.

<requirements>
- `ContextoVaga` (dataclass frozen) em `curriculo/domain/contexto_vaga.py`: `descricao_vaga`, `idioma_alvo`, `analise_vaga`. Invariantes: descrição obrigatória; idioma em {pt, en}.
- `AnaliseVagaSchema` em `entrypoints/api/schemas/vaga.py` com `from_domain`/`to_domain`, usando os nomes dos enums de `vaga/domain/analise_vaga.py`.
- Complexidade: low. Dependências: JOB-0033 concluída.
</requirements>

## Subtarefas

- [ ] 1.1 Testes de `ContextoVaga` e do schema (Red).
- [ ] 1.2 Implementar o Value Object.
- [ ] 1.3 Implementar o schema e exportar.

## Detalhes de Implementação

Ver "Interfaces Principais" e "Modelos de Dados" em `techspec-job-0034.md`.

## Critérios de Sucesso

- Ida e volta `AnaliseVaga` ↔ JSON sem perda.

## Testes da Tarefa

- [ ] Testes de unidade de `ContextoVaga` e de `AnaliseVagaSchema`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/contexto_vaga.py`
- `src/jobsync/entrypoints/api/schemas/vaga.py`
- `src/jobsync/tests/curriculo/test_contexto_vaga.py`
- `src/jobsync/tests/entrypoints/api/`

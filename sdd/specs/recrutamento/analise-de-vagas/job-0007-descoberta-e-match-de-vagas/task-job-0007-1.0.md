# Tarefa 1.0: Modelar domínio (VagaExterna, FonteVagaExterna, VagaComScore)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar as entidades de domínio da Fase 3: `VagaExterna` (uma vaga vinda de uma fonte externa), `FonteVagaExterna` (enum das cinco fontes) e `VagaComScore` (uma vaga já com o resultado do ATS Score calculado).

<requirements>
- `FonteVagaExterna`: enum com `REMOTEOK`, `WE_WORK_REMOTELY`, `ARBEITNOW`, `ADZUNA`, `GOOGLE_CUSTOM_SEARCH`.
- `VagaExterna`: dataclass frozen com `titulo`, `empresa`, `descricao`, `url`, `fonte: FonteVagaExterna`, `descricao_incompleta: bool = False`. Validação de campos obrigatórios (`titulo`, `empresa`, `descricao`, `url` não vazios) em `__post_init__`.
- `VagaComScore`: dataclass frozen com `vaga: VagaExterna` e `resultado_score: ResultadoAtsScore` (reaproveitado de `src/domain/ats_score`, Fase 1).
- Seguir a convenção do projeto: pacote `src/domain/vaga_externa/__init__.py` — complexidade: low.
</requirements>

## Subtarefas

- [ ] 1.1 Criar `src/domain/vaga_externa/__init__.py` com `FonteVagaExterna`, `VagaExterna` e `VagaComScore`.
- [ ] 1.2 Escrever testes unitários para as invariantes de `VagaExterna`.

## Detalhes de Implementação

Consultar a seção "Modelos de Dados" de `techspec-job-0007.md`. Seguir o estilo já usado em `src/domain/vaga/__init__.py` e `src/domain/candidatura/__init__.py`.

## Critérios de Sucesso

- `VagaExterna`, `FonteVagaExterna` e `VagaComScore` são instanciáveis, imutáveis, e `VagaExterna` valida campos obrigatórios.

## Testes da Tarefa

- [ ] Teste unitário: `VagaExterna` com `titulo`, `empresa`, `descricao` ou `url` vazios levanta `ValueError`.
- [ ] Teste unitário: `VagaExterna` válida é instanciável com `descricao_incompleta` default `False`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/domain/vaga_externa/__init__.py`
- `src/tests/domain/vaga_externa/__init__.py`
- `src/tests/domain/vaga_externa/test_vaga_externa.py`

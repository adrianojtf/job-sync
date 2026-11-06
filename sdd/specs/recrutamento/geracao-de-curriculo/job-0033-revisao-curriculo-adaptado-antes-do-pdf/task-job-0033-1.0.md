# Tarefa 1.0: Agregado RascunhoCurriculoAdaptado

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar o agregado de domínio que representa o currículo adaptado em revisão, com as seções como partes do mesmo objeto, e a conversão para o `Curriculo` consumido pelo gerador de PDF.

<requirements>
- Dataclass frozen em `curriculo/domain/rascunho_curriculo_adaptado.py`: `nome_completo`, `email`, `linkedin`, `secoes: tuple[SecaoCurriculo, ...]`, `experiencias: tuple[ExperienciaParaAvaliacao, ...] | None`.
- Invariantes (`ValueError`): nome obrigatório; ao menos uma seção ou experiência; `EXPERIENCIAS` não pode estar em `secoes` quando `experiencias` não for `None`; experiência estruturada exige cargo e empresa.
- `revisado(...)`: monta a partir da edição do usuário, descartando seções e experiências em branco.
- `para_curriculo()`: gera a seção `EXPERIENCIAS` no formato atual (`Cargo — Empresa (Período)\nDescrição`, blocos separados por linha em branco).
- Exportar em `jobsync.curriculo`.
- Complexidade: medium. Dependências: nenhuma.
</requirements>

## Subtarefas

- [ ] 1.1 Escrever os testes (Red) em `tests/curriculo/test_rascunho_curriculo_adaptado.py`.
- [ ] 1.2 Implementar o agregado e as invariantes.
- [ ] 1.3 Implementar `revisado` e `para_curriculo`.
- [ ] 1.4 Exportar em `curriculo/__init__.py`.

## Detalhes de Implementação

Ver "Interfaces Principais" e "Modelos de Dados" em `techspec-job-0033.md`.

## Critérios de Sucesso

- Agregado imutável com invariantes cobertas por testes.
- Formato da seção de experiências idêntico ao de `AdaptarCurriculoParaVaga._montar_secao_experiencias`.

## Testes da Tarefa

- [ ] Testes de unidade de invariantes, `revisado` e `para_curriculo`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/rascunho_curriculo_adaptado.py`
- `src/jobsync/curriculo/__init__.py`
- `src/jobsync/tests/curriculo/test_rascunho_curriculo_adaptado.py`

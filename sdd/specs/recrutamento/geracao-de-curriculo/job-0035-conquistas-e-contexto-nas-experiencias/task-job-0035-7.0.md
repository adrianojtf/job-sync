# Tarefa 7.0: SugestaoIA genérico e formulário

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Generalizar o componente de sugestão e preparar os campos de conquistas e contexto.

<requirements>
- `SugestaoIA<S>` com `descrever` e `aplicar`; `SugestaoCampo` usa `S = string` sem mudar o comportamento.
- `ExperienciaAdaptadaFormulario` e `CAMPOS_EXPERIENCIA_ADAPTADA`.
- Mapeamento lista ↔ linhas e composição para avaliação em `formulario-revisao`.
- Complexidade: medium. Dependências: 6.0.
</requirements>

## Subtarefas

- [ ] 7.1 Testes (Red).
- [ ] 7.2 Componente genérico.
- [ ] 7.3 Campos e mapeamento.

## Detalhes de Implementação

Ver "Componente genérico" e "Modelos de Dados" em `techspec-job-0035.md`.

## Critérios de Sucesso

- Testes atuais de `SugestaoIA` passam sem edição.

## Testes da Tarefa

- [ ] Testes de `SugestaoIA` e de `formulario-revisao`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/`
- `frontend/src/features/ajustar-vaga/formulario-revisao.ts`

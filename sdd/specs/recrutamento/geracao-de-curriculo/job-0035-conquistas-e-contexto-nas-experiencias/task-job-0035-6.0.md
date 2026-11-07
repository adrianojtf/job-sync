# Tarefa 6.0: Cliente de API e tipos

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Atualizar o contrato tipado e o cliente do frontend.

<requirements>
- Regenerar `schema.d.ts` com Python 3.12, o mesmo do CI.
- `sugerirAjusteExperienciaAdaptada` no port e no cliente HTTP, com rota de IA.
- Complexidade: low. Dependências: 5.0.
</requirements>

## Subtarefas

- [ ] 6.1 Regenerar tipos com Python 3.12.
- [ ] 6.2 Método e testes.

## Detalhes de Implementação

Ver "Endpoints de API" em `techspec-job-0035.md`.

## Critérios de Sucesso

- Tipos compilam; o contrato é idêntico ao gerado no CI.

## Testes da Tarefa

- [ ] Testes de unidade de `http-api-client`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/api/`

# Tarefa 8.0: Integração das sugestões em Meu perfil

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Ligar o botão ao resumo e às experiências do cadastro, sem contexto de vaga.

<requirements>
- Botão no resumo e em cada experiência.
- Pedido sem `contexto_vaga`.
- Aplicar não salva o perfil.
- Complexidade: medium. Dependências: 6.0.
</requirements>

## Subtarefas

- [ ] 8.1 Testes (Red).
- [ ] 8.2 Funções em `use-perfil-estruturado`.
- [ ] 8.3 Integrar em `PerfilPage`.

## Detalhes de Implementação

Ver PRD RF7–RF10 e `techspec-job-0034.md`.

## Critérios de Sucesso

- Testes existentes de Meu perfil continuam passando.

## Testes da Tarefa

- [ ] Testes de `PerfilPage`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/perfil/`

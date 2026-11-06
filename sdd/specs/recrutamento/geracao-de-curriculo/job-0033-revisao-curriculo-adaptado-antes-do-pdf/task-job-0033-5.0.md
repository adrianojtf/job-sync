# Tarefa 5.0: Extrair componentes do formulário de "Meu perfil"

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Mover os blocos reutilizáveis do formulário de cadastro para `shared/formulario-curriculo`, sem mudar o comportamento de "Meu perfil".

<requirements>
- `ListaItensCurriculo` genérico no tipo do formulário (substitui `ListaItensPerfil`).
- `PainelDadosPessoais` (nome, e-mail, LinkedIn, resumo).
- `campos-curriculo.ts` com `CAMPOS_EXPERIENCIA`, `EXPERIENCIA_VAZIA`, `ExperienciaFormulario`.
- `FormularioCurriculo.module.css` com os estilos compartilhados.
- `PerfilPage.test.tsx` passa sem alteração.
- Complexidade: medium. Dependências: nenhuma.
</requirements>

## Subtarefas

- [ ] 5.1 Extrair estilos.
- [ ] 5.2 Extrair `ListaItensCurriculo` e campos.
- [ ] 5.3 Extrair `PainelDadosPessoais`.
- [ ] 5.4 Recompor `PerfilPage`.

## Detalhes de Implementação

Ver "Visão Geral dos Componentes" (frontend) e "Decisões Principais" (item 3) em `techspec-job-0033.md`.

## Critérios de Sucesso

- Refatoração pura: testes de `features/perfil` verdes sem edição; lint e build verdes.

## Testes da Tarefa

- [ ] Testes existentes de `features/perfil`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/`
- `frontend/src/features/perfil/`

# Tarefa 7.0: Tela RevisaoCurriculoAdaptado

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar a tela de revisão com todas as seções editáveis e a confirmação única.

<requirements>
- `formulario-revisao.ts`: rascunho ↔ formulário (PERFIL ↔ resumo; experiências estruturadas ou texto).
- Blocos: dados pessoais, experiências, tecnologias, formação, certificações, idiomas (só os presentes).
- Validação no envio; "Confirmar e gerar PDF"; "Voltar para a vaga" com `ConfirmacaoModal` quando houver alterações.
- Erro na geração preserva as edições.
- Complexidade: high. Dependências: 5.0, 6.0.
</requirements>

## Subtarefas

- [ ] 7.1 Testes do mapeamento.
- [ ] 7.2 Mapeamento.
- [ ] 7.3 Testes do componente.
- [ ] 7.4 Componente.

## Detalhes de Implementação

Ver "Formulário de revisão" em `techspec-job-0033.md` e PRD RF6–RF18.

## Critérios de Sucesso

- Todas as seções editáveis simultaneamente; confirmação envia o estado editado.

## Testes da Tarefa

- [ ] Testes de unidade (Vitest) do mapeamento e do componente.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx`
- `frontend/src/features/ajustar-vaga/formulario-revisao.ts`

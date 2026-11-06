# Tarefa 7.0: Integração das sugestões na revisão

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Ligar o botão aos blocos da revisão, com o contexto da vaga.

<requirements>
- Botão no resumo, nas tecnologias e em cada experiência; no bloco de experiências em texto quando a fonte é PDF.
- Sem botão em formação, certificações e idiomas.
- O pedido leva `contexto_vaga` (descrição, idioma e `analise_vaga` guardada com o rascunho).
- Aplicar altera só o campo do bloco e marca o formulário como alterado.
- Complexidade: medium. Dependências: 6.0.
</requirements>

## Subtarefas

- [ ] 7.1 Testes (Red).
- [ ] 7.2 `use-sugestoes-revisao`.
- [ ] 7.3 Integrar em `RevisaoCurriculoAdaptado` e `PainelDadosPessoais`.

## Detalhes de Implementação

Ver "Visão Geral dos Componentes" (frontend) em `techspec-job-0034.md` e PRD RF1–RF6.

## Critérios de Sucesso

- Pedidos com contexto da vaga; testes da revisão da JOB-0033 continuam passando.

## Testes da Tarefa

- [ ] Testes de `RevisaoCurriculoAdaptado` e do hook.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/ajustar-vaga/`
- `frontend/src/shared/formulario-curriculo/PainelDadosPessoais.tsx`

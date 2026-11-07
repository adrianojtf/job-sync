# Tarefa 8.0: Integrar a revisão em AjustarVagaPage

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Trocar a geração direta do PDF pelas etapas vaga → revisão → resultado.

<requirements>
- `use-ajustar-vaga`: `gerarRascunho` e `gerarPdf` no lugar de `adaptar`.
- "Gerar currículo adaptado" abre a revisão; "Baixar PDF" só após confirmar.
- Avaliações da vaga e das experiências continuam visíveis.
- Complexidade: medium. Dependências: 7.0.
</requirements>

## Subtarefas

- [ ] 8.1 Ajustar testes da página (Red).
- [ ] 8.2 Hook.
- [ ] 8.3 Página.

## Detalhes de Implementação

Ver "Decisões Principais" (item 6) em `techspec-job-0033.md`.

## Critérios de Sucesso

- Nenhum PDF gerado sem confirmação no frontend.

## Testes da Tarefa

- [ ] Testes de `AjustarVagaPage`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/ajustar-vaga/AjustarVagaPage.tsx`
- `frontend/src/features/ajustar-vaga/use-ajustar-vaga.ts`

# Tarefa 7.0: SugestaoIA com histórico e foco

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

O botão "Sugestões de IA" passa a enviar a tentativa e as últimas sugestões do bloco e a mostrar o foco usado. Vale para a revisão e para "Meu perfil".

<requirements>
- `SugestaoIA` guarda o histórico do bloco (até 3, aplicadas ou descartadas) e o número da tentativa, só na memória do componente.
- `sugerir(texto, refino)` recebe o refino; a resposta traz o foco.
- O painel mostra "Foco: ..." (rótulos em `rotulos-foco.ts`), dentro da região `aria-live`.
- `use-sugestoes` e `SugestaoExperienciaAdaptada` enviam `refino`; `PerfilPage` segue funcionando.
- O texto do botão não muda.
- Complexidade: medium. Dependências: 6.0.
</requirements>

## Subtarefas

- [x] 7.1 Testes de `SugestaoIA` (Red).
- [x] 7.2 `rotulos-foco.ts`.
- [x] 7.3 `SugestaoIA` e `SugestaoCampo`.
- [x] 7.4 `use-sugestoes` e `SugestaoExperienciaAdaptada`.

## Detalhes de Implementação

Ver componentes de frontend e decisão 5 ("Histórico no frontend") em `techspec-job-0037.md`.

## Critérios de Sucesso

- Segundo pedido envia tentativa 2 e a primeira sugestão; o quinto envia só as 3 últimas.
- O pedido usa sempre o texto atual do campo.

## Testes da Tarefa

- [x] Vitest de `SugestaoIA`, `use-sugestoes`, `SugestaoExperienciaAdaptada` e `PerfilPage`; lint e `tsc`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/shared/formulario-curriculo/{SugestaoIA.tsx,SugestaoCampo.tsx,use-sugestoes.ts,rotulos-foco.ts}`
- `frontend/src/features/ajustar-vaga/SugestaoExperienciaAdaptada.tsx`
- `frontend/src/features/perfil/PerfilPage.tsx`

# Tarefa 7.0: Layout responsivo e visual estilo Jira

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Troca a grade de 4 colunas por colunas de largura fixa em uma área com rolagem, com o visual de boards de mercado, usando os tokens existentes.

<requirements>
- Área do board com rolagem horizontal e `scroll-snap-x`; colunas de 272 px no desktop e `min(85vw, 320px)` no celular; sem empilhar colunas.
- Altura do board com `100dvh` menos o topo; cada coluna rola na vertical e o cabeçalho fica visível (sticky).
- Cabeçalho com nome, contagem e marca de cor (`COR_STATUS`); cartão com título como link, empresa com inicial e tempo relativo.
- Estados de arrasto: cartão levantado com sombra e leve inclinação, espaço reservado na origem, coluna de destino destacada, estado vazio indicando que dá para soltar.
- Cursor de arrasto, realce ao passar o mouse e foco de teclado visível; `prefers-reduced-motion` corta as animações.
- Usar os tokens de `tokens.css`, sem paleta nova; contraste AA.
</requirements>

## Subtarefas

- [ ] 7.1 Estilizar o contêiner do board e as colunas (largura fixa, rolagem, sticky).
- [ ] 7.2 Estilizar o cartão e o cabeçalho com os dados do PRD.
- [ ] 7.3 Estilizar os estados de arrasto e de coluna vazia.
- [ ] 7.4 Cobrir `prefers-reduced-motion` e foco visível.
- [ ] 7.5 Conferir as larguras 375, 768 e 1280 px no navegador.

## Detalhes de Implementação

Techspec: "Decisões Principais" (Layout). PRD: RF19–RF29.

## Critérios de Sucesso

- Sem rolagem horizontal da página inteira em nenhuma largura.
- No celular, a rolagem encaixa uma coluna por vez.
- O visual usa apenas tokens do design system.

## Testes da Tarefa

- [ ] Verificação visual manual nas três larguras (o jsdom não calcula layout).
- [ ] Cobertura automática do layout fica na tarefa 8.0 (E2E).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/candidaturas/CandidaturasPage.module.css`
- frontend/src/shared/ui/tokens.css (apenas conferir)
- frontend/src/app/AppShell.module.css (apenas conferir a altura útil)

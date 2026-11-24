# Resumo de Tarefas de Implementação das Listas Compactas e Reordenáveis no Perfil (JOB-0046)

## Tarefas

- [x] 1.0 Backend: Periodo, limite de itens e validação no SalvarPerfilEstruturadoInputValidator
- [x] 2.0 Frontend: periodo.ts, limites.ts e validação por campo
- [x] 3.0 Toast com ação e duração, e histórico do formulário (desfazer)
- [x] 4.0 ListaItensCurriculo em modo cartão com reordenação, limite e ordenar por período
- [x] 5.0 Cartões abertos lembrados e modo linha única para idiomas
- [x] 6.0 Tecnologias como tags reordenáveis
- [x] 7.0 Aviso ao sair: hook, componente e aplicação nas telas do escopo
- [ ] 8.0 Integração em Meu perfil: as cinco listas, validações e aviso ao sair
- [ ] 9.0 E2E das listas reordenáveis e acessibilidade

## Dependências

- Depende da JOB-0009 e da JOB-0045, já integradas na branch.
- 1.0, 3.0 e 7.0 não dependem de outra tarefa e podem ser feitas em paralelo.
- 2.0 depende da 1.0 (tabela compartilhada de casos).
- 4.0 depende da 2.0 e da 3.0.
- 5.0 depende da 4.0.
- 6.0 depende da 3.0 e pode andar em paralelo com a 4.0.
- 8.0 depende da 1.0, 4.0, 5.0, 6.0 e 7.0.
- 9.0 depende da 8.0.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Backend: Periodo, limite de itens e validação no SalvarPerfilEstruturadoInputValidator | medium | nenhuma | Testes de `TestPeriodo` (tabela de casos) |
| 2.0 | Frontend: periodo.ts, limites.ts e validação por campo | low | 1.0 | Vitest de `periodo.ts` |
| 3.0 | Toast com ação e duração, e histórico do formulário (desfazer) | low | nenhuma | Vitest de `Toast`/`ToastProvider` |
| 4.0 | ListaItensCurriculo em modo cartão com reordenação, limite e ordenar por período | high | 2.0, 3.0 | Vitest de `ListaItensCurriculo` e `CartaoDaLista` |
| 5.0 | Cartões abertos lembrados e modo linha única para idiomas | medium | 4.0 | Vitest de `use-cartoes-abertos` (storage ausente ou com erro, item removido) |
| 6.0 | Tecnologias como tags reordenáveis | medium | 3.0 | Vitest de `ListaDeTecnologias` e de `formulario-perfil` |
| 7.0 | Aviso ao sair: hook, componente e aplicação nas telas do escopo | medium | nenhuma | Vitest do hook e das telas |
| 8.0 | Integração em Meu perfil: as cinco listas, validações e aviso ao sair | high | 1.0, 4.0, 5.0, 6.0, 7.0 | Vitest de `PerfilPage` e `formulario-perfil` |
| 9.0 | E2E das listas reordenáveis e acessibilidade | medium | 8.0 | Playwright em `frontend/e2e` |

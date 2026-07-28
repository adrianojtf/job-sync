# Resumo de Tarefas de Implementação de Persistência, Perfil e Login Simples

## Tarefas

- [x] 1.0 Modelar entidades de domínio Perfil e CurriculoSalvo
- [x] 2.0 Definir portas RepositorioPerfilPort e RepositorioCurriculoSalvoPort
- [x] 3.0 Implementar RepositorioSqlite (schema + ambas as portas) com testes de integração
- [x] 4.0 Implementar use case EntrarOuCriarPerfil com testes unitários
- [x] 5.0 Implementar use cases da biblioteca de currículos (SalvarCurriculo, ListarCurriculosSalvos, RemoverCurriculoSalvo) com testes unitários
- [x] 6.0 Integrar login por identificador e biblioteca de currículos na UI Streamlit
- [x] 7.0 Validação manual end-to-end e execução da suíte completa de testes

## Dependências

- 1.0 deve ser concluída antes de 2.0.
- 2.0 deve ser concluída antes de 3.0.
- 3.0 deve ser concluída antes de 4.0 e 5.0 (podem ser feitas em paralelo entre si).
- 4.0 e 5.0 devem ser concluídas antes de 6.0.
- 6.0 deve ser concluída antes de 7.0.

## Entregáveis principais

- Entidades de domínio `Perfil` e `CurriculoSalvo`, imutáveis e sem dependência de infraestrutura.
- Persistência local em SQLite (`storage/job_sync.db`) para perfis e currículos salvos, isolada por perfil.
- Login simples por identificador (sem senha), criando o perfil automaticamente no primeiro acesso.
- Biblioteca de currículos por perfil, com limite de 10 currículos salvos e opção de remoção.
- Tela de entrada e biblioteca de currículos integradas ao fluxo Streamlit já existente, sem alterar o caso de uso `AdaptarCurriculoParaVaga`.

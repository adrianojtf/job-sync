# Tarefa 4.0: Use cases SalvarPerfilEstruturado e BuscarPerfilEstruturado

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar os dois use cases básicos de persistência do perfil: salvar (criar ou atualizar) e buscar por identificador de perfil.

<requirements>
- `SalvarPerfilEstruturado`: pacote com `dtos.py` (`SalvarPerfilEstruturadoInputDto` com todos os campos de `PerfilEstruturado`), `validator.py` (exige `perfil_identificador`, `nome_completo` e `email` não vazios), `use_case.py` (`executar(input_dto) -> PerfilEstruturado`, monta a entidade e chama `repositorio.salvar`), `__init__.py`.
- `BuscarPerfilEstruturado`: pacote sem DTO (mesmo padrão de `EntrarOuCriarPerfil`) — `executar(perfil_identificador: str) -> PerfilEstruturado | None`, chama `repositorio.buscar_por_perfil`.
- Nenhum dos dois use cases chama outro use case.
- Complexidade: low.
</requirements>

## Subtarefas

- [ ] 4.1 Criar pacote `src/application/use_cases/salvar_perfil_estruturado/` (`dtos.py`, `use_case.py`, `validator.py`, `__init__.py`).
- [ ] 4.2 Criar pacote `src/application/use_cases/buscar_perfil_estruturado/` (`use_case.py`, `__init__.py`).
- [ ] 4.3 Escrever testes de `SalvarPerfilEstruturado` com fake do repositório, cobrindo validação de campos obrigatórios.
- [ ] 4.4 Escrever testes de `BuscarPerfilEstruturado` com fake do repositório, cobrindo perfil existente e inexistente.

## Detalhes de Implementação

Consultar a seção "Interfaces Principais" de `techspec-job-0009.md`. Seguir o estilo de `src/application/use_cases/salvar_curriculo/` (com DTO) e `src/application/use_cases/entrar_ou_criar_perfil/` (sem DTO).

## Critérios de Sucesso

- `SalvarPerfilEstruturado.executar` persiste corretamente e rejeita input inválido (campos obrigatórios vazios).
- `BuscarPerfilEstruturado.executar` retorna o perfil salvo, ou `None` se não existir.

## Testes da Tarefa

- [ ] Teste unitário: `SalvarPerfilEstruturado` com dados válidos chama `repositorio.salvar` com o `PerfilEstruturado` correto.
- [ ] Teste unitário: `SalvarPerfilEstruturado` com `nome_completo`, `email` ou `perfil_identificador` vazios levanta `ValueError`.
- [ ] Teste unitário: `BuscarPerfilEstruturado` retorna o perfil quando existente, `None` quando não.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/application/use_cases/salvar_perfil_estruturado/dtos.py`
- `src/application/use_cases/salvar_perfil_estruturado/use_case.py`
- `src/application/use_cases/salvar_perfil_estruturado/validator.py`
- `src/application/use_cases/salvar_perfil_estruturado/__init__.py`
- `src/application/use_cases/buscar_perfil_estruturado/use_case.py`
- `src/application/use_cases/buscar_perfil_estruturado/__init__.py`
- `src/tests/application/use_cases/salvar_perfil_estruturado/test_use_case.py`
- `src/tests/application/use_cases/buscar_perfil_estruturado/test_use_case.py`

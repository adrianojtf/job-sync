# Tarefa 2.0: Definir portas RepositorioVagaPort e RepositorioCandidaturaPort

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Definir as interfaces de aplicação para persistência de vagas capturadas e candidaturas, seguindo o mesmo padrão das portas da Fase 0 (`RepositorioPerfilPort`, `RepositorioCurriculoSalvoPort`).

<requirements>
- `RepositorioVagaPort`: `salvar(vaga) -> Vaga`, `listar_nao_convertidas(perfil_identificador) -> tuple[Vaga, ...]`.
- `RepositorioCandidaturaPort`: `salvar(candidatura) -> Candidatura`, `listar_por_perfil(perfil_identificador) -> tuple[Candidatura, ...]`, `atualizar_status(candidatura_id, novo_status) -> Candidatura`.
- Interfaces puras (`ABC` + `@abstractmethod`) — complexidade: low.
</requirements>

## Subtarefas

- [x] 2.1 Criar `application/ports/repositorio_vaga_port.py` com `RepositorioVagaPort`.
- [x] 2.2 Criar `application/ports/repositorio_candidatura_port.py` com `RepositorioCandidaturaPort`.
- [x] 2.3 Escrever testes confirmando que ambas são interfaces puras, usando um fake concreto (mesmo padrão de `tests/application/test_repositorio_perfil_port.py`).

## Detalhes de Implementação

Consultar a seção "Interfaces Principais" de `techspec-job-0006.md`.

## Critérios de Sucesso

- As duas portas compilam e podem ser implementadas por dublês de teste sem depender de SQLite.

## Testes da Tarefa

- [x] Teste unitário: fake de `RepositorioVagaPort` salva e lista vagas não convertidas corretamente.
- [x] Teste unitário: fake de `RepositorioCandidaturaPort` salva, lista e atualiza status corretamente.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `application/ports/repositorio_vaga_port.py`
- `application/ports/repositorio_candidatura_port.py`
- `tests/application/test_repositorio_vaga_port.py`
- `tests/application/test_repositorio_candidatura_port.py`

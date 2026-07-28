# Tarefa 4.0: Implementar use case EntrarOuCriarPerfil

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o caso de uso que resolve o login simples: recebe um identificador, retorna o `Perfil` existente ou cria um novo automaticamente, sem exigir senha.

<requirements>
- Se o identificador já existe (via `RepositorioPerfilPort.buscar_por_identificador`), retornar o `Perfil` existente sem duplicar.
- Se o identificador não existe, criar um novo `Perfil` via `RepositorioPerfilPort.criar`.
- Não introduzir nenhuma validação de senha ou autenticação além do identificador — complexidade: low.
</requirements>

## Subtarefas

- [x] 4.1 Criar `application/use_cases/entrar_ou_criar_perfil.py` com a classe `EntrarOuCriarPerfil`, recebendo `RepositorioPerfilPort` no construtor (Dependency Injection, mesmo padrão de `AdaptarCurriculoParaVaga`).
- [x] 4.2 Implementar o método `executar(identificador: str) -> Perfil` com a lógica de buscar-ou-criar.
- [x] 4.3 Escrever testes unitários usando um fake de `RepositorioPerfilPort` (seguindo o padrão de dublês de `tests/application/test_adaptar_curriculo_para_vaga.py`).

## Detalhes de Implementação

Consultar a seção "Visão Geral dos Componentes" de `techspec-job-0004.md` para a responsabilidade exata do use case.

## Critérios de Sucesso

- Primeiro acesso com um identificador novo cria o perfil automaticamente.
- Acessos subsequentes com o mesmo identificador retornam sempre o mesmo perfil, sem duplicação.

## Testes da Tarefa

- [x] Teste unitário: identificador novo cria perfil via `RepositorioPerfilPort.criar`.
- [x] Teste unitário: identificador existente retorna o perfil sem chamar `criar`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `application/use_cases/entrar_ou_criar_perfil.py`
- `tests/application/test_entrar_ou_criar_perfil.py`

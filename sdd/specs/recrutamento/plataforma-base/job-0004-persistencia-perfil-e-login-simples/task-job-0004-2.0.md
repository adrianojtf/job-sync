# Tarefa 2.0: Definir portas RepositorioPerfilPort e RepositorioCurriculoSalvoPort

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Definir as interfaces de aplicação (Ports) que isolam os use cases da Fase 0 de qualquer detalhe de persistência concreta, seguindo o mesmo padrão de Dependency Inversion já usado em `application/ports/gerador_pdf_port.py` e `application/ports/job_description_analyzer_port.py`.

<requirements>
- `RepositorioPerfilPort` deve expor `buscar_por_identificador` e `criar`.
- `RepositorioCurriculoSalvoPort` deve expor `salvar`, `listar_por_perfil`, `remover` e `contar_por_perfil` (necessário para a regra de limite de 10 na Tarefa 5.0).
- Ambas as portas devem ser `ABC` com métodos `@abstractmethod`, sem nenhuma implementação concreta nesta tarefa — complexidade: low.
</requirements>

## Subtarefas

- [x] 2.1 Criar `application/ports/repositorio_perfil_port.py` com a interface `RepositorioPerfilPort`.
- [x] 2.2 Criar `application/ports/repositorio_curriculo_salvo_port.py` com a interface `RepositorioCurriculoSalvoPort`.

## Detalhes de Implementação

Consultar a seção "Interfaces Principais" de `techspec-job-0004.md` para a assinatura exata de cada método. Seguir o estilo de `application/ports/job_description_analyzer_port.py` (docstring explicando o contrato esperado da implementação concreta).

## Critérios de Sucesso

- As duas portas compilam e podem ser implementadas por um dublê de teste (fake) sem depender de nenhuma biblioteca de banco de dados.

## Testes da Tarefa

- [x] Teste unitário (seguindo o padrão de `tests/application/test_job_description_analyzer_port.py`): confirmar que `RepositorioPerfilPort` e `RepositorioCurriculoSalvoPort` são interfaces puras (não instanciáveis diretamente).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `application/ports/repositorio_perfil_port.py`
- `application/ports/repositorio_curriculo_salvo_port.py`
- `tests/application/test_repositorio_perfil_port.py`
- `tests/application/test_repositorio_curriculo_salvo_port.py`

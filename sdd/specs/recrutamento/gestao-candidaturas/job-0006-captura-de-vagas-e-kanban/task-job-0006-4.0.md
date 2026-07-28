# Tarefa 4.0: Implementar use cases de vaga (CapturarVaga, ListarVagasCapturadas)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar os casos de uso que criam uma `Vaga` (a partir de captura via extensão ou colagem manual) e listam as vagas ainda não convertidas em candidatura.

<requirements>
- `CapturarVaga` recebe `perfil_identificador`, `texto_descricao`, `url_origem` (opcional) e persiste uma nova `Vaga` com `data_captura` atual e id gerado (`uuid4`).
- `ListarVagasCapturadas` retorna as vagas não convertidas de um perfil, via `RepositorioVagaPort.listar_nao_convertidas` — complexidade: low.
</requirements>

## Subtarefas

- [x] 4.1 Criar `application/use_cases/capturar_vaga.py` com a classe `CapturarVaga`.
- [x] 4.2 Criar `application/use_cases/listar_vagas_capturadas.py` com a classe `ListarVagasCapturadas`.
- [x] 4.3 Escrever testes unitários para ambos usando fake de `RepositorioVagaPort`.

## Detalhes de Implementação

Consultar a seção "Visão Geral dos Componentes" de `techspec-job-0006.md`. Seguir o padrão de geração de id via `uuid.uuid4()` já usado em `application/use_cases/salvar_curriculo.py` (Fase 0).

## Critérios de Sucesso

- `CapturarVaga` persiste corretamente uma nova vaga associada ao perfil.
- `ListarVagasCapturadas` retorna apenas vagas do perfil informado.

## Testes da Tarefa

- [x] Teste unitário: `CapturarVaga` gera id único e persiste `texto_descricao`, `url_origem` e `data_captura`.
- [x] Teste unitário: `ListarVagasCapturadas` retorna apenas vagas do perfil informado.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `application/use_cases/capturar_vaga.py`
- `application/use_cases/listar_vagas_capturadas.py`
- `tests/application/test_capturar_vaga.py`
- `tests/application/test_listar_vagas_capturadas.py`

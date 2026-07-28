# Tarefa 5.0: Implementar use cases da biblioteca de currículos

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar os três casos de uso que compõem a biblioteca de currículos por perfil: salvar (com limite de 10), listar e remover.

<requirements>
- `SalvarCurriculo` deve bloquear o salvamento quando `RepositorioCurriculoSalvoPort.contar_por_perfil` já retornar 10 para o perfil, levantando um erro claro (PRD, requisito funcional 7).
- `ListarCurriculosSalvos` deve retornar os currículos do perfil ordenados por `data_upload` decrescente (mais recente primeiro).
- `RemoverCurriculoSalvo` deve impedir a remoção de um currículo que não pertença ao perfil informado.
- Complexidade: medium (a regra de limite e o isolamento por perfil exigem atenção redobrada nos testes).
</requirements>

## Subtarefas

- [x] 5.1 Criar `application/use_cases/salvar_curriculo.py` com a classe `SalvarCurriculo`, aplicando a regra de limite de 10 antes de persistir.
- [x] 5.2 Criar `application/use_cases/listar_curriculos_salvos.py` com a classe `ListarCurriculosSalvos`.
- [x] 5.3 Criar `application/use_cases/remover_curriculo_salvo.py` com a classe `RemoverCurriculoSalvo`, validando que o currículo pertence ao perfil antes de remover.
- [x] 5.4 Escrever testes unitários para os três use cases usando um fake de `RepositorioCurriculoSalvoPort`.

## Detalhes de Implementação

Consultar a seção "Visão Geral dos Componentes" de `techspec-job-0004.md` e os requisitos funcionais 5-9 do `prd-job-0004.md` para a regra de limite e o comportamento esperado de cada use case.

## Critérios de Sucesso

- Um perfil nunca consegue ter mais de 10 currículos salvos simultaneamente.
- A tentativa de remover currículo de outro perfil falha de forma explícita, sem exceção genérica.
- A listagem reflete corretamente a ordenação por data de upload.

## Testes da Tarefa

- [x] Teste unitário: `SalvarCurriculo` com perfil já no limite de 10 levanta erro e não chama `salvar`.
- [x] Teste unitário: `SalvarCurriculo` com perfil abaixo do limite persiste normalmente.
- [x] Teste unitário: `ListarCurriculosSalvos` retorna ordenado por data decrescente.
- [x] Teste unitário: `RemoverCurriculoSalvo` rejeita remoção de currículo de outro perfil.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `application/use_cases/salvar_curriculo.py`
- `application/use_cases/listar_curriculos_salvos.py`
- `application/use_cases/remover_curriculo_salvo.py`
- `tests/application/test_salvar_curriculo.py`
- `tests/application/test_listar_curriculos_salvos.py`
- `tests/application/test_remover_curriculo_salvo.py`

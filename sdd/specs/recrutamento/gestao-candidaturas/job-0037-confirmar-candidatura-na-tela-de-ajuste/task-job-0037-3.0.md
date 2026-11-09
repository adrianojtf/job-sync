# Tarefa 3.0: Caso de uso ConfirmarCandidaturaAjustada

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o caso de uso que cria, de uma vez, o currículo salvo com o PDF gerado, a vaga e a candidatura em `APLICADO`, sem deixar registros pela metade.

<requirements>
- Criar o pacote `candidatura/service_layer/confirmar_candidatura_ajustada/` com `service.py`, `dtos.py`, `validator.py` e `__init__.py`, no padrão dos outros casos de uso.
- `ConfirmarCandidaturaAjustadaInputDto`: `perfil_identificador`, `cargo`, `empresa`, `descricao_vaga`, `nome_arquivo`, `pdf_bytes`.
- O validador recusa campos vazios e PDF que não começa com `%PDF`, com `ValueError` e mensagens em português.
- `ConfirmarCandidaturaAjustada` recebe `CandidaturaRepository`, `VagaRepository` e `CurriculoSalvoRepository` e não chama outro caso de uso.
- Ordem de `executar`: validar; `contar_por_perfil` e `garantir_espaco`; salvar `CurriculoSalvo` (`nome_referencia` = `nome_arquivo`); salvar `Vaga`; `marcar_como_convertida`; salvar a `Candidatura` com `Candidatura.nova`. A vaga é convertida antes da candidatura para nada ficar visível em "Vagas salvas" se a candidatura falhar (RF 7).
- Sem espaço na biblioteca, nenhum repositório é gravado.
- Se salvar a vaga, marcá-la como convertida ou salvar a candidatura falhar, remover o currículo salvo, registrar `WARNING` (sem dados pessoais) e relançar o erro original.
- Se a remoção do currículo também falhar, registrar `WARNING` e relançar o erro original, não o da remoção.
- `INFO` com identificadores e o tamanho do PDF em bytes, sem conteúdo.
- Exportar o caso de uso, o DTO e o validador em `service_layer/confirmar_candidatura_ajustada/__init__.py`, como em `criar_candidatura` (o `candidatura/__init__.py` exporta só o domínio).
</requirements>

## Subtarefas

- [x] 3.1 Escrever os testes com repositórios fake (red).
- [x] 3.2 Criar DTO e validador.
- [x] 3.3 Implementar o caso de uso na ordem definida.
- [x] 3.4 Implementar a compensação e o tratamento da falha em `marcar_como_convertida`.
- [x] 3.5 Exportar no `__init__.py` do caso de uso e conferir os contratos com `lint-imports`.

## Detalhes de Implementação

Consultar em `techspec-job-0037.md` as seções "Interfaces Principais" (ordem e compensação) e "Considerações Técnicas > Riscos Conhecidos".

## Critérios de Sucesso

- Uma confirmação válida cria exatamente um currículo salvo, uma vaga e uma candidatura `APLICADO`, ligados por identificador.
- A vaga criada não aparece em `listar_nao_convertidas`.
- Biblioteca cheia ou erro intermediário não deixam nada visível ao usuário: sem currículo, sem candidatura e sem vaga em "Vagas salvas".
- `lint-imports` sem ciclo entre `candidatura`, `vaga` e `curriculo_salvo`.

## Testes da Tarefa

- [x] Confirmação válida cria currículo, vaga e candidatura com empresa, cargo e `curriculo_salvo_id` corretos.
- [x] A vaga fica convertida e fora de `listar_nao_convertidas`.
- [x] Biblioteca com 10 currículos levanta `LimiteCurriculosSalvosExcedido` e não grava nada nos três repositórios.
- [x] Falha ao salvar a vaga remove o currículo salvo.
- [x] Falha ao marcar a vaga como convertida remove o currículo salvo.
- [x] Falha ao salvar a candidatura remove o currículo salvo e deixa a vaga convertida, fora de "Vagas salvas".
- [x] Falha ao remover o currículo na compensação não esconde o erro original e registra `WARNING`.
- [x] Validação: perfil, cargo, empresa, descrição e nome do arquivo vazios; PDF sem `%PDF`; PDF vazio.
- [x] O log não contém a descrição da vaga nem o conteúdo do PDF.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/candidatura/service_layer/confirmar_candidatura_ajustada/` (novo)
- `src/jobsync/candidatura/service_layer/criar_candidatura/` (referência)
- `src/jobsync/curriculo_salvo/domain/limite_curriculos_salvos.py` (tarefa 1.0)
- `src/jobsync/candidatura/adapters/candidatura_repository_fake.py`
- `src/jobsync/tests/candidatura/`
- `setup.cfg` (contratos do import-linter)

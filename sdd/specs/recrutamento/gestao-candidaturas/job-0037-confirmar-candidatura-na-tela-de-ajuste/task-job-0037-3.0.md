# Tarefa 3.0: Caso de uso ConfirmarCandidaturaAjustada

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o caso de uso que cria, de uma vez, o currículo salvo com o PDF gerado, a vaga e a candidatura em `APLICADO`, sem deixar registros pela metade.

<requirements>
- Criar o pacote `candidatura/service_layer/confirmar_candidatura_ajustada/` com `service.py`, `dtos.py`, `validator.py` e `__init__.py`, no padrão dos outros casos de uso.
- `ConfirmarCandidaturaAjustadaInputDto`: `perfil_identificador`, `cargo`, `empresa`, `descricao_vaga`, `nome_arquivo`, `pdf_bytes`.
- O validador recusa campos vazios e PDF que não começa com `%PDF`, com `ValueError` e mensagens em português.
- `ConfirmarCandidaturaAjustada` recebe `CandidaturaRepository`, `VagaRepository` e `CurriculoSalvoRepository` e não chama outro caso de uso.
- Ordem de `executar`: validar; `contar_por_perfil` e `garantir_espaco`; salvar `CurriculoSalvo` (`nome_referencia` = `nome_arquivo`); salvar `Vaga`; salvar a `Candidatura` com `Candidatura.nova`; `marcar_como_convertida`.
- Sem espaço na biblioteca, nenhum repositório é gravado.
- Se salvar a vaga ou a candidatura falhar, remover o currículo salvo e relançar o erro.
- Se `marcar_como_convertida` falhar, manter a candidatura, registrar `WARNING` (sem dados pessoais) e devolver a candidatura.
- `INFO` com identificadores e o tamanho do PDF em bytes, sem conteúdo.
- Exportar o caso de uso em `candidatura/__init__.py`.
</requirements>

## Subtarefas

- [ ] 3.1 Escrever os testes com repositórios fake (red).
- [ ] 3.2 Criar DTO e validador.
- [ ] 3.3 Implementar o caso de uso na ordem definida.
- [ ] 3.4 Implementar a compensação e o tratamento da falha em `marcar_como_convertida`.
- [ ] 3.5 Exportar em `candidatura/__init__.py` e conferir os contratos com `lint-imports`.

## Detalhes de Implementação

Consultar em `techspec-job-0037.md` as seções "Interfaces Principais" (ordem e compensação) e "Considerações Técnicas > Riscos Conhecidos".

## Critérios de Sucesso

- Uma confirmação válida cria exatamente um currículo salvo, uma vaga e uma candidatura `APLICADO`, ligados por identificador.
- A vaga criada não aparece em `listar_nao_convertidas`.
- Biblioteca cheia ou erro intermediário não deixam currículo, vaga ou candidatura sobrando (exceto o caso documentado do passo final).
- `lint-imports` sem ciclo entre `candidatura`, `vaga` e `curriculo_salvo`.

## Testes da Tarefa

- [ ] Confirmação válida cria currículo, vaga e candidatura com empresa, cargo e `curriculo_salvo_id` corretos.
- [ ] A vaga fica convertida e fora de `listar_nao_convertidas`.
- [ ] Biblioteca com 10 currículos levanta `LimiteCurriculosSalvosExcedido` e não grava nada nos três repositórios.
- [ ] Falha ao salvar a vaga remove o currículo salvo.
- [ ] Falha ao salvar a candidatura remove o currículo salvo.
- [ ] Falha em `marcar_como_convertida` mantém a candidatura e registra `WARNING`.
- [ ] Validação: perfil, cargo, empresa, descrição e nome do arquivo vazios; PDF sem `%PDF`; PDF vazio.
- [ ] O log não contém a descrição da vaga nem o conteúdo do PDF.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/candidatura/service_layer/confirmar_candidatura_ajustada/` (novo)
- `src/jobsync/candidatura/__init__.py`
- `src/jobsync/candidatura/service_layer/criar_candidatura/` (referência)
- `src/jobsync/curriculo_salvo/domain/limite_curriculos_salvos.py` (tarefa 1.0)
- `src/jobsync/candidatura/adapters/candidatura_repository_fake.py`
- `src/jobsync/tests/candidatura/`
- `setup.cfg` (contratos do import-linter)

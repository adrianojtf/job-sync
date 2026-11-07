# Tarefa 2.0: Caso de uso GerarPdfCurriculoRevisado

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar o caso de uso de confirmação: recebe o rascunho revisado e gera o PDF e o nome do arquivo, dependendo apenas de `GeradorPdfPort`.

<requirements>
- Pacote `curriculo/service_layer/gerar_pdf_curriculo_revisado` com `service.py`, `dtos.py`, `validator.py`, `__init__.py`.
- Extrair as validações de idioma, cargo e empresa para `curriculo/service_layer/validacoes_vaga_alvo.py`, usadas também por `AdaptarCurriculoParaVagaInputValidator`.
- `NomeArquivo` usa o nome completo revisado.
- Log INFO sem dados pessoais (contagens e idioma).
- Complexidade: medium. Dependências: 1.0.
</requirements>

## Subtarefas

- [ ] 2.1 Testes do caso de uso (Red).
- [ ] 2.2 Extrair validações comuns.
- [ ] 2.3 Implementar DTOs, validator e service.

## Detalhes de Implementação

Ver "Interfaces Principais" em `techspec-job-0033.md`.

## Critérios de Sucesso

- O PDF é gerado a partir do conteúdo editado (mock de `GeradorPdfPort` recebe o `Curriculo` revisado).
- Testes existentes do validator de adaptação continuam passando.

## Testes da Tarefa

- [ ] Testes de unidade do service e das validações.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/service_layer/gerar_pdf_curriculo_revisado/`
- `src/jobsync/curriculo/service_layer/validacoes_vaga_alvo.py`
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/validator.py`
- `src/jobsync/tests/curriculo/test_gerar_pdf_curriculo_revisado_service.py`

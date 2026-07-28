# Tarefa 9.0: Validação manual end-to-end e execução da suíte completa de testes

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Fechar a Fase 2 validando o fluxo completo — capturar uma vaga real via extensão, ver na lista do Streamlit, criar candidatura e movê-la pelo Kanban — e garantir que toda a suíte de testes do projeto continua passando.

<requirements>
- Rodar `pytest tests/ -v` e confirmar que todos os testes passam (Fases 0, 1 e 2).
- Rodar `ServidorCaptura` e `ui/app_streamlit.py` simultaneamente e validar a captura de ponta a ponta.
- Validar manualmente o menu lateral e o Kanban — complexidade: low.
</requirements>

## Subtarefas

- [x] 9.1 Executar `pytest tests/ -v` e corrigir qualquer regressão encontrada.
- [x] 9.2 Subir `ServidorCaptura` (`uvicorn infrastructure.api.servidor_captura:app --port 8502`) e `streamlit run ui/app_streamlit.py` simultaneamente.
- [x] 9.3 Carregar a extensão Chrome, configurar o token, capturar uma página de teste.
- [x] 9.4 Confirmar que a vaga aparece na página "Vagas & Candidaturas", criar uma candidatura e movê-la entre as 4 colunas do Kanban.

## Detalhes de Implementação

Não há detalhes técnicos novos nesta tarefa — é a validação final consolidando as Tarefas 1.0 a 8.0 conforme `techspec-job-0006.md`.

## Critérios de Sucesso

- Suíte de testes 100% verde.
- Fluxo de captura → lista → candidatura → Kanban validado manualmente de ponta a ponta.

## Testes da Tarefa

- [x] `pytest tests/ -v` sem falhas.
- [x] Roteiro manual de captura e Kanban executado com sucesso.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `tests/` (suíte completa)

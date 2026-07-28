# Tarefa 7.0: Validação manual end-to-end e execução da suíte completa de testes

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Fechar a Fase 0 validando o fluxo completo (login → biblioteca → adaptação) rodando de ponta a ponta, e garantir que toda a suíte de testes do projeto (existente + nova) continua passando.

<requirements>
- Rodar `pytest tests/ -v` e confirmar que todos os testes (existentes e novos das Tarefas 1.0-5.0) passam.
- Validar manualmente a persistência: dados devem sobreviver ao encerrar e reiniciar o processo Streamlit.
- Confirmar isolamento entre perfis também pela UI, não só pelos testes de integração (criar dois perfis distintos e confirmar que não compartilham currículos) — complexidade: low.
</requirements>

## Subtarefas

- [x] 7.1 Executar `pytest tests/ -v` e corrigir qualquer regressão encontrada.
- [x] 7.2 Validar manualmente: encerrar `streamlit run ui/app_streamlit.py`, reabrir, confirmar que os currículos salvos anteriormente ainda aparecem.
- [x] 7.3 Validar manualmente com dois identificadores diferentes que os currículos de um perfil não aparecem para o outro.
- [x] 7.4 Atualizar `README.md`/`README-macos.md` com o novo passo de execução, se necessário (ex: nenhuma nova variável de ambiente é exigida nesta fase).

## Detalhes de Implementação

Não há detalhes técnicos novos nesta tarefa — é a validação final consolidando as Tarefas 1.0 a 6.0 conforme `techspec-job-0004.md`.

## Critérios de Sucesso

- Suíte de testes 100% verde.
- Persistência confirmada manualmente entre reinicializações do processo.
- Isolamento entre perfis confirmado manualmente pela UI.

## Testes da Tarefa

- [x] `pytest tests/ -v` sem falhas.
- [x] Roteiro manual de persistência e isolamento executado com sucesso.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `tests/` (suíte completa)
- `README.md`, `README-macos.md` (se necessário)

# Tarefa 7.0: Validação manual end-to-end e execução da suíte completa de testes

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Fechar a Fase 1 validando o fluxo completo (adaptação → ATS Score → carta de apresentação) e garantindo que toda a suíte de testes do projeto (existente + Fase 0 + Fase 1) continua passando.

<requirements>
- Rodar `pytest tests/ -v` e confirmar que todos os testes passam.
- Validar manualmente com uma vaga e currículo reais que a nota de ATS Score bate com a lista de requisitos explícitos exibida.
- Validar manualmente que a carta de apresentação gerada não inventa fatos ausentes do currículo original — complexidade: low.
</requirements>

## Subtarefas

- [x] 7.1 Executar `pytest tests/ -v` e corrigir qualquer regressão encontrada.
- [x] 7.2 Validar manualmente: gerar adaptação com uma vaga real, conferir nota e requisitos faltantes.
- [x] 7.3 Validar manualmente: revisar o texto da carta de apresentação gerada, confirmando fidelidade aos fatos do currículo.

## Detalhes de Implementação

Não há detalhes técnicos novos nesta tarefa — é a validação final consolidando as Tarefas 1.0 a 6.0 conforme `techspec-job-0005.md`.

## Critérios de Sucesso

- Suíte de testes 100% verde.
- Nota de ATS Score e carta de apresentação corretas e coerentes, validadas manualmente com um caso real.

## Testes da Tarefa

- [x] `pytest tests/ -v` sem falhas.
- [x] Roteiro manual de ATS Score e carta de apresentação executado com sucesso.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `tests/` (suíte completa)

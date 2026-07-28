# Tarefa 9.0: Validação manual end-to-end e execução da suíte completa de testes

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Validar o fluxo completo do Perfil Estruturado — criação manual, importação de PDF, e uso automático nas três funcionalidades existentes — e garantir que toda a suíte de testes automatizados (Fases 0-3 + este job) continua passando.

<requirements>
- Rodar `pytest src/tests/ -v` e confirmar que todos os testes passam, incluindo os novos desta fase.
- Validar manualmente: criar um perfil do zero, salvar, editar, salvar de novo.
- Validar manualmente: importar de um PDF real (currículo salvo na biblioteca ou export do LinkedIn), revisar/editar os campos pré-preenchidos, salvar.
- Validar manualmente: com perfil preenchido, usar "Adaptar Currículo", "Analisar ATS" e "Candidatar" sem fazer upload de PDF.
- Validar manualmente: sem perfil preenchido, confirmar que as três funcionalidades continuam funcionando com upload de PDF, exatamente como antes desta fase.
- Complexidade: low.
</requirements>

## Subtarefas

- [ ] 9.1 Rodar a suíte completa e confirmar 100% de sucesso.
- [ ] 9.2 Validar manualmente a criação e edição do perfil.
- [ ] 9.3 Validar manualmente a importação de PDF.
- [ ] 9.4 Validar manualmente o uso automático do perfil nas três funcionalidades existentes.
- [ ] 9.5 Validar manualmente que o fluxo de upload de PDF continua funcionando sem perfil preenchido.
- [ ] 9.6 Marcar todas as tarefas como concluídas em `resumo-tasks-job-0009.md`.

## Detalhes de Implementação

Consultar a seção "Riscos Conhecidos" de `techspec-job-0009.md` para os pontos de atenção na validação manual (formatos de PDF incomuns na extração estruturada).

## Critérios de Sucesso

- Suíte de testes 100% verde.
- Fluxo completo (criar/editar/importar perfil, e uso automático nas três funcionalidades existentes) validado manualmente.

## Testes da Tarefa

- [ ] `pytest src/tests/ -v` sem falhas.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/plataforma-base/job-0009-perfil-estruturado-curriculo-mestre/resumo-tasks-job-0009.md`

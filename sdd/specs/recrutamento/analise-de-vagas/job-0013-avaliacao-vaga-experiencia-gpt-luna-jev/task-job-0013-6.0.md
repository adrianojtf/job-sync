# Tarefa 6.0: Finalizar composição, configuração e regressão

<critical>Ler `prd-job-0013.md` e `techspec-job-0013.md` desta pasta antes de iniciar a tarefa.</critical>

## Visão Geral

Concluir a configuração dos provedores na composição do projeto, atualizar as instruções para desenvolvedores e validar a integração completa sem depender de chamadas reais nos testes automatizados.

<requirements>
- Injetar os clientes OpenAI e Jev pela composição da API e atualizar os pontos atuais de composição do Streamlit para o cliente OpenAI, sem adicionar telas novas.
- Atualizar `.env.example` com `OPENAI_API_KEY`, `OPENAI_MODEL`, `TYPESAFE_API_KEY` e o modelo Jev configurado.
- Remover referências operacionais a Groq/GROQ_API_KEY após confirmar que nenhum consumidor de produção restante depende delas.
- Documentar configuração, credenciais, novos endpoints e limitações das avaliações no README.
- Executar a suíte completa e a verificação de arquitetura/imports.
</requirements>

## Subtarefas

- [x] 6.1 Centralizar a criação e injeção dos clientes nos pontos de composição existentes.
- [x] 6.2 Atualizar `.env.example`, dependências e instruções de configuração sem incluir segredos.
- [x] 6.3 Documentar endpoints, score 0–100, limitações de avaliação factual e suporte automático apenas a perfil estruturado.
- [x] 6.4 Executar pytest, `import-linter` e revisar chamadas restantes a Groq e dados sensíveis em logs.

## Detalhes de Implementação

Consultar as seções de integração, observabilidade e riscos em `techspec-job-0013.md`. Os testes automatizados devem usar fakes; a validação manual com provedores reais requer configuração local segura e não deve ser condição para testes unitários.

## Critérios de Sucesso

- Configuração de ambiente descreve os dois provedores sem credenciais reais.
- O README corresponde aos endpoints e comportamento implementados.
- A suíte completa e a verificação de arquitetura passam.
- Nenhum texto de currículo ou descrição de vaga é registrado nos logs.

## Testes da Tarefa

- [x] Executar a suíte completa de testes pytest.
- [x] Executar `import-linter` conforme configuração do projeto.
- [x] Verificar geração do OpenAPI e contratos dos endpoints novos e alterados.
- [x] Confirmar que buscas por `ClienteGroq` e `GROQ_API_KEY` não encontram usos de produção remanescentes.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/entrypoints/api/dependencies.py`
- `src/jobsync/entrypoints/streamlit_app.py`
- `src/jobsync/entrypoints/api/main.py`
- `.env.example`
- `requirements.txt`
- `README.md`
- `src/jobsync/tests/`

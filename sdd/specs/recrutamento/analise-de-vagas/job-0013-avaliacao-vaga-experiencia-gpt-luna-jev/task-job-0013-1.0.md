# Tarefa 1.0: Migrar os adapters atuais para GPT-6 Luna

<critical>Ler `prd-job-0013.md` e `techspec-job-0013.md` desta pasta antes de iniciar a tarefa.</critical>

## Visão Geral

Substituir a integração Groq usada atualmente pelas operações de IA existentes pela API oficial da OpenAI com o modelo GPT-6 Luna, preservando os formatos e comportamentos observáveis dos adapters.

<requirements>
- Criar um cliente OpenAI centralizado que use a Responses API e o modelo configurável `gpt-6-luna`.
- Migrar os seis consumidores atuais de `ClienteGroq`: ajuste e extração de currículo, análise de requisitos da vaga, geração de carta, sugestões ATS e extração de perfil estruturado.
- Manter as avaliações novas de vaga e experiência fora desta migração; elas serão atendidas pelo Jev.
- Remover a dependência Groq quando nenhum consumidor de produção depender mais dela.
- Não realizar chamadas reais à OpenAI nos testes automatizados.
</requirements>

## Subtarefas

- [x] 1.1 Implementar `ClienteOpenAI` com leitura de `OPENAI_API_KEY` e `OPENAI_MODEL`, tratamento de resposta JSON e erros do SDK.
- [x] 1.2 Migrar cada adapter consumidor de `ClienteGroq`, mantendo contratos de entrada e saída.
- [x] 1.3 Atualizar dependências Python, removendo `groq` e adicionando o SDK `openai`.
- [x] 1.4 Atualizar ou substituir os testes existentes para usar fakes do cliente OpenAI.

## Detalhes de Implementação

Seguir os pontos de integração e a lista de adapters em `techspec-job-0013.md`. Manter a análise de requisitos técnicos da vaga em GPT-6 Luna; a validação de qualidade da descrição será uma operação Jev independente.

## Critérios de Sucesso

- Todos os seis consumidores atuais usam `ClienteOpenAI`; não há import de produção do SDK Groq.
- O modelo pode ser configurado sem alteração de código e o padrão é `gpt-6-luna`.
- Os adapters preservam seus contratos e reportam respostas inválidas/erros sem expor segredos.

## Testes da Tarefa

- [x] Testes unitários do cliente para configuração, parsing JSON e erros do SDK usando fakes.
- [x] Testes existentes de cada adapter migrado passam sem chamadas de rede.
- [x] Busca no código confirma que `ClienteGroq` não é mais usado em produção.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/shared_kernel/adapters/cliente_groq_client.py`
- Novo `src/jobsync/shared_kernel/adapters/cliente_openai_client.py`
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/adapters/extrator_curriculo_client.py`
- `src/jobsync/curriculo/adapters/gerar_carta_apresentacao_client.py`
- `src/jobsync/curriculo/adapters/gerar_sugestoes_ats_client.py`
- `src/jobsync/perfil_estruturado/adapters/extrator_perfil_estruturado_client.py`
- `src/jobsync/vaga/adapters/job_description_analyzer_client.py`
- `requirements.txt` e testes dos adapters migrados

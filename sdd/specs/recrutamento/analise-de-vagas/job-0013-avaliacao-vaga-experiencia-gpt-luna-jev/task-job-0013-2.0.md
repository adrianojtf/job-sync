# Tarefa 2.0: Criar a integração e os modelos de avaliação Jev

<critical>Ler `prd-job-0013.md` e `techspec-job-0013.md` desta pasta antes de iniciar a tarefa.</critical>

## Visão Geral

Adicionar a integração TypeSafe AI e os contratos de domínio compartilhados necessários para avaliar descrições de vagas e experiências com decisões estruturadas, sem geração de explicações livres.

<requirements>
- Criar um cliente TypeSafe centralizado com o SDK Python oficial, chave `TYPESAFE_API_KEY` e modelo configurável com padrão `jev-1.14.0`.
- Criar resultados de domínio distintos para avaliação de descrição de vaga e de experiência profissional.
- Representar cada dimensão com score normalizado de 0 a 100 e categoria/nível fixo.
- Normalizar os níveis Jev de 0 a 4 para 0 a 100 e calcular o score geral como média aritmética das dimensões.
- Traduzir erros e respostas inválidas do SDK para exceções controladas, sem registrar conteúdo enviado.
</requirements>

## Subtarefas

- [x] 2.1 Adicionar o pacote `typesafe-sdk` e implementar `ClienteJev`.
- [x] 2.2 Criar os modelos de avaliação, os tipos de dimensão e a estrutura `ExperienciaParaAvaliacao`.
- [x] 2.3 Implementar a conversão de primitivas `Score`, incluindo score geral, níveis e confiança.
- [x] 2.4 Cobrir configuração, mapeamento, normalização e erros com testes usando fakes.

## Detalhes de Implementação

As portas específicas e os adapters de domínio podem ser concluídos junto com os casos de uso das tarefas 3.0 e 4.0. Usar rubricas positivas para todas as dimensões, inclusive inclusão e consistência textual. A avaliação de consistência não pode afirmar verificação factual externa.

## Critérios de Sucesso

- O cliente envia perguntas tipadas e recebe dados estruturados sem parsing de prosa gerada.
- Scores de dimensão ficam no intervalo 0–100 e o agregado é determinístico.
- A chave e o conteúdo de currículo/vaga não aparecem nos logs.

## Testes da Tarefa

- [x] Testar os limites 0 e 4, valores intermediários, arredondamento e média agregada.
- [x] Testar campos ausentes, resposta inválida, timeout e falha de autenticação com fakes.
- [x] Não usar credenciais nem chamadas de modelo reais.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- Novo `src/jobsync/shared_kernel/adapters/cliente_jev_client.py`
- Novos modelos e portas em `src/jobsync/vaga/domain/` e `src/jobsync/curriculo/domain/`
- `requirements.txt`
- Novos testes nos diretórios `src/jobsync/tests/vaga/` e `src/jobsync/tests/curriculo/`

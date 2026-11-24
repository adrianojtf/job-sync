# Tarefa 3.0: Extrator por IA e leitor genérico de páginas de vaga

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar `ExtratorDadosVagaIaClient` (texto para `DadosVaga`) e `LeitorVagaGenericoClient` (link de sites que não são o LinkedIn).

Complexidade: medium. Dependências: 1.0, 2.0.

<requirements>
- O extrator usa `ClienteOpenAI.solicitar_json`. O prompt trata o texto como dado, nunca como instrução, e não inventa valores.
- Truncar o texto em 20.000 caracteres e validar tipo e tamanho da saída antes de montar `DadosVaga`.
- A descrição devolvida é o texto original, sem resumo nem tradução.
- O leitor genérico busca a página pelo `ClienteHttpSeguro`, lê o JSON-LD `JobPosting` e, na falta dele, envia o texto da página ao extrator.
- Falhas de rede ou bloqueio viram `LeituraVagaIndisponivel` com motivo.
</requirements>

## Subtarefas

- [ ] 3.1 Escrever os testes do extrator com `ClienteOpenAI` falso (JSON inválido, tipos errados, texto com instruções embutidas).
- [ ] 3.2 Implementar `ExtratorDadosVagaIaClient`.
- [ ] 3.3 Escrever os testes do leitor genérico (JSON-LD válido, inválido, fallback para IA, bloqueio).
- [ ] 3.4 Implementar `LeitorVagaGenericoClient`.
- [ ] 3.5 Exportar os adapters em `vaga/adapters/__init__.py`.

## Detalhes de Implementação

Seguir o padrão de `vaga/adapters/job_description_analyzer_client.py` para prompt e tratamento de `ValueError`. Ver "Pontos de Integração" da techspec.

## Critérios de Sucesso

- Um JSON-LD `JobPosting` válido preenche cargo, empresa, local e descrição sem chamar a IA.
- Texto com instruções embutidas não altera o formato da saída.

## Testes da Tarefa

- [ ] Testes de unidade: `TestExtratorDadosVagaIaClient`, `TestLeitorVagaGenericoClient`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/prd-job-0047.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/techspec-job-0047.md`
- `src/jobsync/vaga/adapters/job_description_analyzer_client.py`
- `src/jobsync/shared_kernel/adapters/cliente_openai_client.py`
- `src/jobsync/tests/vaga/`

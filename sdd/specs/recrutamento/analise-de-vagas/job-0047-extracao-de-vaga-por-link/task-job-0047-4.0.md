# Tarefa 4.0: Leitor do LinkedIn pela versão pública da vaga

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar `LeitorVagaLinkedInClient`, que monta a URL pública de visitante a partir do id da vaga e interpreta o HTML de forma determinística (sem IA).

Complexidade: medium. Dependências: 1.0, 2.0.

<requirements>
- Uma única requisição por link. Sem repetição após 429 ou desafio anti-bot.
- Sem rotação de IP, falsificação de navegador, resolução de desafios ou uso de credenciais.
- Extrair cargo, empresa, local, descrição (texto original, com listas e parágrafos preservados) e, quando existirem, tipo de contratação, senioridade e setor.
- Não guardar número de candidatos, tempo de publicação nem dados de terceiros.
- Se faltar título ou descrição, levantar `LeituraVagaIndisponivel` (sem acionar a IA).
- 429, desafio, 404 e tempo esgotado viram `LeituraVagaIndisponivel` com motivo (`bloqueado`, `nao_encontrada`, `tempo_esgotado`, `sem_dados`).
- O interpretador de HTML fica isolado em uma classe, com fixture de teste.
</requirements>

## Subtarefas

- [ ] 4.1 Criar a fixture de HTML reduzida e anonimizada, baseada na estrutura real da resposta de visitante.
- [ ] 4.2 Escrever os testes (campos completos, sem campos secundários, HTML sem título, 429, 404).
- [ ] 4.3 Implementar o interpretador de HTML (BeautifulSoup) e a conversão de `<br>` e `<li>` para linhas.
- [ ] 4.4 Implementar `LeitorVagaLinkedInClient`.
- [ ] 4.5 Exportar o adapter em `vaga/adapters/__init__.py`.

## Detalhes de Implementação

Ver "Pontos de Integração" e "Riscos Conhecidos" da techspec. Usa o `ClienteHttpSeguro` da task 2.0. O caminho de visitante não é documentado pelo LinkedIn: concentrar a URL e as classes em constantes do adapter.

## Critérios de Sucesso

- A fixture gera `DadosVaga` com descrição em português, sem resumo (critério 8 do PRD).
- Bloqueio nunca gera repetição de requisição.

## Testes da Tarefa

- [ ] Testes de unidade: `TestLeitorVagaLinkedInClient`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/prd-job-0047.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/techspec-job-0047.md`
- `src/jobsync/vaga/adapters/`
- `src/jobsync/tests/vaga/fixtures/`

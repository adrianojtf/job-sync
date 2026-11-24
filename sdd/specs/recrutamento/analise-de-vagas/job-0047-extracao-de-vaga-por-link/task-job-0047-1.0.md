# Tarefa 1.0: Domínio: `LinkVaga`, `DadosVaga`, exceções e portas

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar, em `vaga/domain`, os objetos de valor `LinkVaga` e `DadosVaga`, as exceções do fluxo e as portas `LeitorVagaPorLinkPort`, `ExtratorDadosVagaDeTextoPort` e `LimitadorLeituraVagaPort`. Camada sem I/O, base das demais tasks.

Complexidade: medium. Dependências: nenhuma.

<requirements>
- `LinkVaga` aceita só `http` e `https`, remove parâmetros de rastreamento e fragmentos, e identifica a fonte (`FonteVaga.LINKEDIN` ou `OUTRA`).
- Para o LinkedIn, extrair o id de `/jobs/view/{slug}-{id}`, `/jobs/view/{id}` e `currentJobId`. Sem id válido, levantar `LinkVagaInvalido`.
- `DadosVaga` é imutável, exige `descricao` e limita o tamanho dos campos de texto.
- Exceções: `LinkVagaInvalido`, `FonteVagaNaoSuportada`, `LeituraVagaIndisponivel`, `LimiteLeituraVagaExcedido`.
- Exportar os novos tipos em `jobsync/vaga/__init__.py`.
- O `domain` usa apenas biblioteca padrão (`urllib.parse`).
</requirements>

## Subtarefas

- [x] 1.1 Escrever os testes de `LinkVaga` (normalização, rastreamento, ids do LinkedIn, esquemas inválidos).
- [x] 1.2 Implementar `LinkVaga` e `FonteVaga`.
- [x] 1.3 Escrever os testes e implementar `DadosVaga`.
- [x] 1.4 Criar as exceções do domínio.
- [x] 1.5 Criar as três portas.
- [x] 1.6 Exportar os tipos em `vaga/__init__.py` e rodar `lint-imports`.

## Detalhes de Implementação

Ver "Componentes" e "Modelos de Dados" da techspec. Seguir o estilo de `vaga/domain/vaga.py` (dataclass imutável com `__post_init__`).

## Critérios de Sucesso

- Todos os casos de normalização do PRD (critérios 2 e 3) passam.
- `lint-imports` continua passando.

## Testes da Tarefa

- [x] Testes de unidade: `TestLinkVaga`, `TestDadosVaga`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/prd-job-0047.md`
- `sdd/specs/recrutamento/analise-de-vagas/job-0047-extracao-de-vaga-por-link/techspec-job-0047.md`
- `src/jobsync/vaga/domain/vaga.py`
- `src/jobsync/vaga/__init__.py`
- `src/jobsync/tests/vaga/`

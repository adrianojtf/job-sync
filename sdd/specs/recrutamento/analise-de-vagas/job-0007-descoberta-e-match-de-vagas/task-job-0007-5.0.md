# Tarefa 5.0: Implementar use case CandidatarNaVagaExterna

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o use case que roda por trás do botão "Candidatar": em um único clique, extrai o currículo, analisa a vaga, adapta todas as seções do currículo, calcula o ATS Score e gera a carta de apresentação, retornando os artefatos prontos (PDF + carta) e a URL original da vaga.

<requirements>
- `CandidatarNaVagaExterna.executar(input_dto: CandidatarNaVagaExternaInputDto) -> CandidatarNaVagaExternaOutputDto`.
- `InputDto`: `pdf_curriculo: bytes`, `vaga: VagaExterna`, `idioma_alvo: str`, `cargo_alvo: str`, `empresa_alvo: str`, `data_referencia: date | None = None`.
- `OutputDto`: `pdf_bytes`, `nome_arquivo`, `resultado_ats: ResultadoAtsScore`, `carta_apresentacao: str`, `url_vaga: str`.
- Depende diretamente de `ExtratorCurriculoPort`, `JobDescriptionAnalyzerPort`, `AjustadorTextoPort`, `GeradorPdfPort`, `CalcularAtsScore` (Domain Service) e `GerarCartaApresentacaoPort` — NÃO chama `AdaptarCurriculoParaVaga` nem `GerarCartaApresentacao` (regra do projeto: use case nunca chama outro use case).
- Fluxo interno replica a lógica de ajuste de seções já usada em `AdaptarCurriculoParaVaga` (mesmo padrão de duplicação já usado por `AnalisarAtsVaga`).
- `url_vaga` no output é o mesmo valor de `vaga.url` do input, repassado sem alteração — usado pela UI para abrir a vaga original em nova aba.
- Complexidade: medium.
</requirements>

## Subtarefas

- [ ] 5.1 Criar pacote `src/application/use_cases/candidatar_na_vaga_externa/` (`dtos.py`, `use_case.py`, `validator.py`, `__init__.py`).
- [ ] 5.2 Implementar a extração, análise da vaga e ajuste de todas as seções do currículo.
- [ ] 5.3 Implementar a geração do PDF adaptado e do nome de arquivo padronizado (`NomeArquivo`).
- [ ] 5.4 Implementar o cálculo do ATS Score e a geração da carta de apresentação.
- [ ] 5.5 Escrever testes usando fakes das portas (mesmos fakes já usados nos testes de `AdaptarCurriculoParaVaga` e `GerarCartaApresentacao`).

## Detalhes de Implementação

Consultar a seção "Fluxo de dados do 'Candidatar'" de `techspec-job-0007.md`.

## Critérios de Sucesso

- `CandidatarNaVagaExterna.executar` retorna PDF adaptado, `ResultadoAtsScore`, carta de apresentação e a `url_vaga` original, sem chamar outro use case.

## Testes da Tarefa

- [ ] Teste unitário: output contém PDF adaptado, `ResultadoAtsScore` e carta de apresentação coerentes com os fakes injetados.
- [ ] Teste unitário: `url_vaga` do output é idêntica a `vaga.url` do input.
- [ ] Teste unitário: validação de input rejeita `pdf_curriculo` vazio.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/application/use_cases/candidatar_na_vaga_externa/dtos.py`
- `src/application/use_cases/candidatar_na_vaga_externa/use_case.py`
- `src/application/use_cases/candidatar_na_vaga_externa/validator.py`
- `src/application/use_cases/candidatar_na_vaga_externa/__init__.py`
- `src/tests/application/use_cases/candidatar_na_vaga_externa/test_use_case.py`

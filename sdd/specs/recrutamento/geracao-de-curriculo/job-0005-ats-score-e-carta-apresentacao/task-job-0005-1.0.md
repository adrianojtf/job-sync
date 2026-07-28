# Tarefa 1.0: Modelar ResultadoAtsScore e implementar CalcularAtsScore

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o cálculo do ATS Score como lógica pura (sem IA), comparando os requisitos técnicos explícitos de uma `AnaliseVaga` com o conteúdo das seções de um `Curriculo` já adaptado.

<requirements>
- `ResultadoAtsScore` deve expor `nota: int` (0-100) e `requisitos_faltantes: tuple[RequisitoTecnico, ...]`.
- `CalcularAtsScore` deve considerar apenas `RequisitoTecnico` com `tipo == TipoRequisitoTecnico.EXPLICITO`.
- Um requisito é "coberto" se seu `nome` (normalizado, case-insensitive) aparece em algum `conteudo` de `SecaoCurriculo`.
- Se não houver requisitos explícitos, a nota deve ser 100 (nada a cobrir).
- Nenhuma chamada a `ClienteGroq` ou qualquer porta externa — complexidade: low.
</requirements>

## Subtarefas

- [x] 1.1 Criar `domain/ats_score.py` com o dataclass `ResultadoAtsScore`.
- [x] 1.2 Criar `application/use_cases/calcular_ats_score.py` com a classe `CalcularAtsScore` e o método `executar(curriculo, analise_vaga) -> ResultadoAtsScore`.
- [x] 1.3 Implementar a normalização de nomes (case-insensitive) usada na comparação entre requisito e conteúdo da seção.
- [x] 1.4 Escrever testes unitários cobrindo cobertura total, parcial, zero requisitos explícitos e case-insensitivity.

## Detalhes de Implementação

Consultar a seção "Design de Implementação > Modelos de Dados" de `techspec-job-0005.md` para a regra exata de cálculo (`nota = round(100 * cobertos / total_explicitos)`).

## Critérios de Sucesso

- `CalcularAtsScore` retorna nota e lista de requisitos faltantes corretas para os cenários de teste.
- Nenhuma dependência de infraestrutura (IA, rede) introduzida.

## Testes da Tarefa

- [x] Teste unitário: currículo cobre todos os requisitos explícitos → nota 100, lista de faltantes vazia.
- [x] Teste unitário: currículo cobre parte dos requisitos → nota proporcional, faltantes corretos.
- [x] Teste unitário: vaga sem requisitos explícitos (só implícitos/ambíguos) → nota 100.
- [x] Teste unitário: comparação de nomes é case-insensitive (ex: "python" cobre requisito "Python").

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `domain/ats_score.py`
- `application/use_cases/calcular_ats_score.py`
- `tests/domain/test_ats_score.py`
- `tests/application/test_calcular_ats_score.py`

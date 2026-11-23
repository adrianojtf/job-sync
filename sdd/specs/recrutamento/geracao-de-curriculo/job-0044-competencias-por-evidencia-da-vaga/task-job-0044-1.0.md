# Tarefa 1.0: `SelecaoDeCompetencias` e `limitar_ao_teto` (domínio puro)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cria o serviço de domínio que decide o que entra em Competências e o corte pelo teto, sem I/O.

Complexidade: low.

<requirements>
- `SelecaoDeCompetencias.selecionar` devolve `ResultadoDaSelecao` (permitidos e lacunas) conforme as regras da techspec.
- Só requisitos `TECNOLOGIA` e `FERRAMENTA` da vaga são considerados; os demais nunca entram nem viram lacuna.
- Permitidos: itens do candidato, requisitos da vaga citados nas experiências (`menciona_tecnologia`) e o alvo das equivalências aplicadas; sem diferenciar caixa, sem duplicatas, na ordem do candidato.
- `limitar_ao_teto` (teto padrão 45) remove primeiro os itens não relevantes, a partir do fim; categoria vazia some; ordem preservada.
</requirements>

## Subtarefas

- [ ] 1.1 Testes de `selecionar`: perfil puro, lacuna, evidência em experiência, equivalência, requisito de habilidade ignorado, caixa, duplicatas, ordem (red).
- [ ] 1.2 Testes de `limitar_ao_teto` (red).
- [ ] 1.3 Implementar `curriculo/domain/selecao_de_competencias.py` e exportar pelo pacote `curriculo` (green).
- [ ] 1.4 Refatorar.

## Detalhes de Implementação

Techspec: "Design de Implementação" e "Abordagem de Testes". PRD: requisitos funcionais correspondentes.

## Critérios de Sucesso

- Os requisitos acima passam nos testes da tarefa.
- Nenhuma regressão nas JOB-0037, JOB-0040 e JOB-0041.

## Testes da Tarefa

- [ ] Testes de unidade do domínio.
- [ ] Regressão: `src/jobsync/tests/curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/selecao_de_competencias.py` (novo)
- `src/jobsync/curriculo/domain/plano_adaptacao.py`
- `src/jobsync/curriculo/domain/equivalencia_tecnologia.py`
- `src/jobsync/curriculo/domain/competencias.py`
- `src/jobsync/tests/curriculo/`

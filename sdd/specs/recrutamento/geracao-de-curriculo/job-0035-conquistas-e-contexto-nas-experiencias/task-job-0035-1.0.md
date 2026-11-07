# Tarefa 1.0: ExperienciaAdaptada e refatoração do rascunho

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar o VO que representa uma experiência adaptada com conquistas e contexto, e fazer o agregado do rascunho guardá-lo no lugar da descrição em texto.

<requirements>
- `ExperienciaAdaptada` (dataclass frozen) em `curriculo/domain/experiencia_adaptada.py`: `cargo`, `empresa`, `periodo`, `conquistas: tuple[str, ...]`, `contexto: str = ""`.
- Invariantes (`ValueError`): cargo e empresa obrigatórios; conquistas sem itens em branco.
- `revisada(...)`: apara e descarta conquistas em branco.
- `para_texto(rotulo_contexto)`: `Cargo — Empresa (Período)`, um `- conquista` por linha e `Rótulo: contexto` ao final; sem linhas vazias nem rótulo solto.
- `para_avaliacao()`: `ExperienciaParaAvaliacao` com a descrição composta (bullets + contexto, sem cabeçalho e sem rótulo).
- `rotulos_experiencia.py`: `ROTULO_CONTEXTO` (`pt` → Contexto, `en` → Context) e o conjunto de rótulos reconhecidos.
- `RascunhoCurriculoAdaptado.experiencias` passa a `tuple[ExperienciaAdaptada, ...] | None`; `para_curriculo(idioma_alvo)` sem valor padrão; `revisado()` descarta experiências totalmente em branco; a validação de cargo e empresa sai do rascunho.
- Atualizar os consumidores diretos para a suíte continuar verde (adaptação, geração do PDF, schemas, routers e app de E2E), mantendo o comportamento até as próximas tasks.
- Complexidade: medium. Dependências: PR 45 (JOB-0033 e JOB-0034).
</requirements>

## Subtarefas

- [ ] 1.1 Testes de `ExperienciaAdaptada` e dos rótulos (Red).
- [ ] 1.2 Implementar o VO e os rótulos.
- [ ] 1.3 Ajustar os testes do rascunho (Red) e refatorar o agregado.
- [ ] 1.4 Ajustar os consumidores e rodar a suíte completa.

## Detalhes de Implementação

Ver "Interfaces Principais" e "Modelos de Dados" em `techspec-job-0035.md`.

## Critérios de Sucesso

- `para_texto` gera exatamente o padrão do PRD (RF14 a RF16) nos dois idiomas.
- O formato do cabeçalho continua o de hoje, porque o PDF o reconhece.
- Suíte de backend verde sem mudar contratos fora do previsto.

## Testes da Tarefa

- [ ] Testes de unidade do VO, dos rótulos e do rascunho.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/experiencia_adaptada.py`
- `src/jobsync/curriculo/domain/rotulos_experiencia.py`
- `src/jobsync/curriculo/domain/rascunho_curriculo_adaptado.py`
- `src/jobsync/tests/curriculo/test_experiencia_adaptada.py`
- `src/jobsync/tests/curriculo/test_rascunho_curriculo_adaptado.py`

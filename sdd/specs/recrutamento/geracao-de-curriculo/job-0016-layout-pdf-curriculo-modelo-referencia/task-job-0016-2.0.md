# Tarefa 2.0: InterpretadorExperiencias e BlocoExperiencia

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar a lógica pura que converte o texto da seção de experiências (ou de formação) em blocos estruturados: empresa, período, cargo, tópicos e contexto. Sem ReportLab. É a peça que permite desenhar empresa e período na mesma linha e os tópicos `-` como lista.

<requirements>
- `BlocoExperiencia` deve ser um dataclass frozen com `empresa`, `periodo`, `cargo`, `topicos: tuple[str, ...]` e `contexto`.
- `InterpretadorExperiencias.interpretar(conteudo) -> list[BlocoExperiencia]`, com blocos separados por linha em branco.
- O período deve ser reconhecido no fim da primeira linha, nos formatos da techspec (mês en/pt, `MM/AAAA`, `AAAA`; fim com `Present`, `Presente`, `Atual`, `Current`, `Hoje`; separadores `-`, `–`, `—`).
- O período entre parênteses no fim da linha (formato do Perfil Estruturado) também deve ser reconhecido.
- Sem período reconhecido: `empresa` recebe a linha inteira e `periodo` fica vazio.
- Tópicos: linhas iniciadas por `-`, `•`, `●` ou `*`, sem o marcador.
- Contexto: linha iniciada por `Context:` ou `Contexto:` (case-insensitive) e linhas soltas que não são tópicos.
- Nenhuma linha de entrada pode ser descartada.
- Reaproveitar a regra de `_parece_posicao_experiencia` para identificar o cargo (DRY).
</requirements>

## Subtarefas

- [ ] 2.1 Escrever os testes de `InterpretadorExperiencias` cobrindo os casos da techspec (red).
- [ ] 2.2 Implementar `BlocoExperiencia`.
- [ ] 2.3 Implementar a regex de período e a separação empresa/período.
- [ ] 2.4 Implementar a classificação de linhas (cargo, tópico, contexto).
- [ ] 2.5 Refatorar mantendo os testes verdes.

## Detalhes de Implementação

Consultar em `techspec-job-0016.md` a seção "Regras de interpretação de experiências".

## Critérios de Sucesso

- Todos os casos extremos do PRD (experiência sem tópicos, sem contexto, sem período, tópico longo) são interpretados sem erro.
- A concatenação de todos os campos dos blocos contém todo o texto da entrada.

## Testes da Tarefa

- [ ] Separa `Starian` e `Mar 2026 - Present`.
- [ ] Separa `SIPPulse - High-Performance NGN SIP Solutions` e `Nov 2022 - Mar 2026` (hífen no nome da empresa não confunde a regex).
- [ ] Reconhece período entre parênteses: `Software Engineer — Starian (Mar 2026 - Present)`.
- [ ] Linha sem período retorna `periodo == ""`.
- [ ] Reconhece cargo na segunda linha.
- [ ] Reconhece tópicos com `-`, `•` e `●`.
- [ ] Reconhece contexto com `Context:` e `Contexto:`.
- [ ] Bloco só com contexto e bloco sem contexto.
- [ ] Vários blocos separados por linha em branco.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/adapters/pdf/interpretador_experiencias.py` (novo)
- `src/jobsync/tests/curriculo/test_interpretador_experiencias.py` (novo)
- `src/jobsync/curriculo/adapters/gerador_pdf_client.py` (referência: `_parece_posicao_experiencia`, `_separar_blocos_experiencias`)
- `src/jobsync/perfil_estruturado/domain/montar_curriculo_do_perfil_estruturado_service.py` (referência de formato de entrada)

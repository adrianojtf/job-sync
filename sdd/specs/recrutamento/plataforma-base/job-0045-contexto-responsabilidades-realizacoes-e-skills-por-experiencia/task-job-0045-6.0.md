# Tarefa 6.0: ExperienciaAdaptada com os quatro blocos, rascunho e serializador na versão 2

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

O currículo adaptado passa a carregar responsabilidades e skills por experiência e é salvo em um formato versionado que continua lendo os dados antigos.

<requirements>
- `ExperienciaAdaptada`: `responsabilidades` e `skills` (padrão vazio); `tem_conteudo`, `revisada`, `como_descricao`, `para_texto` e `para_avaliacao` consideram os quatro blocos.
- `para_texto` segue a convenção da task 1.0, com os rótulos do idioma.
- `ExperienciaEditada` e `RascunhoCurriculoAdaptado.para_curriculo` com os quatro blocos.
- `ExperienciaParaAvaliacao` ganha `contexto`, `responsabilidades` e `skills`.
- `VERSAO_DO_FORMATO = 2`; o leitor aceita as versões 1 e 2 (a 1 vem com blocos novos vazios); versão desconhecida continua rejeitada.
- Skills das experiências ausentes nas competências entram na categoria "Tecnologias" do adaptado (PRD RF 24).
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 6.1 Escrever os testes do domínio e do serializador (red).
- [ ] 6.2 Implementar os campos e as conversões (green).
- [ ] 6.3 Implementar a versão 2 e a leitura da versão 1 (green).
- [ ] 6.4 Refatorar e rodar `tests/curriculo` e `tests/curriculo_adaptado`.

## Detalhes de Implementação

Techspec: "Modelos de Dados" (`ExperienciaAdaptada`, JSON do currículo adaptado). PRD: RF 21 a 25.

Complexidade: medium. Dependências: 1.0.

## Critérios de Sucesso

- Currículos adaptados já salvos (versão 1) abrem sem erro.
- O texto gerado por `para_texto` é lido de volta pelo interpretador da task 1.0 sem perda.

## Testes da Tarefa

- [ ] Testes de `TestExperienciaAdaptada` e `TestRascunhoCurriculoAdaptado`.
- [ ] Testes do `serializador_conteudo` (ida e volta v2, leitura v1, versão desconhecida).
- [ ] Regressão: `src/jobsync/tests/curriculo/` e `src/jobsync/tests/curriculo_adaptado/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/experiencia_adaptada.py`
- `src/jobsync/curriculo/domain/rascunho_curriculo_adaptado.py`
- `src/jobsync/curriculo/domain/avaliacao_experiencia.py`
- `src/jobsync/curriculo_adaptado/adapters/serializador_conteudo.py`
- `src/jobsync/tests/curriculo/test_experiencia_adaptada.py`
- `src/jobsync/tests/curriculo/test_rascunho_curriculo_adaptado.py`
- `src/jobsync/tests/curriculo_adaptado/exemplos.py`

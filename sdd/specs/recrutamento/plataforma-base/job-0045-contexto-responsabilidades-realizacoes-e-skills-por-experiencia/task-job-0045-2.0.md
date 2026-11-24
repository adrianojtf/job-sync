# Tarefa 2.0: Domínio do perfil: quatro blocos por experiência e sincronia de skills

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

`ExperienciaProfissional` ganha contexto, responsabilidades e skills (as realizações reaproveitam `conquistas`), e `PerfilEstruturado` passa a sincronizar as skills com as tecnologias gerais.

<requirements>
- `ExperienciaProfissional`: `contexto: str = ""`, `responsabilidades: tuple[str, ...] = ()`, `skills: tuple[str, ...] = ()`; `conquistas` mantém o nome.
- Invariantes: sem item vazio e sem skill duplicada (`normalizar_texto`); limites de 3 a 5 itens não são invariante.
- `eh_legada`: tem `descricao` e nenhum dos quatro blocos.
- `PerfilEstruturado.tecnologias_ausentes()` e `com_tecnologias_das_experiencias()`: comparam sem diferenciar maiúsculas e espaços, incluem no fim da lista plana, não duplicam e nunca removem (PRD RF 16 a 20).
- `DadosPerfilExtraidos` herda os campos novos sem alteração própria.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [ ] 2.1 Escrever os testes de `ExperienciaProfissional` e `PerfilEstruturado` (red).
- [ ] 2.2 Implementar os campos, as invariantes e `eh_legada` (green).
- [ ] 2.3 Implementar a sincronia de skills (green).
- [ ] 2.4 Refatorar e rodar `tests/perfil_estruturado`.

## Detalhes de Implementação

Techspec: "Modelos de Dados" (`ExperienciaProfissional`) e "Interfaces Principais" (`tecnologias_ausentes`, `com_tecnologias_das_experiencias`). PRD: RF 1 a 5 e 16 a 20.

Complexidade: medium. Dependências: nenhuma.

## Critérios de Sucesso

- Skills das experiências ausentes nas tecnologias gerais são incluídas sem duplicar; excluir a skill da experiência não remove a tecnologia geral.
- Código existente que cria `ExperienciaProfissional` sem os campos novos continua funcionando.

## Testes da Tarefa

- [ ] Testes de `TestExperienciaProfissional` (invariantes, `eh_legada`).
- [ ] Testes de `TestPerfilEstruturado` (sincronia: maiúsculas, espaços, já existente, vazio).
- [ ] Regressão: `src/jobsync/tests/perfil_estruturado/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/perfil_estruturado/domain/perfil_estruturado.py`
- `src/jobsync/perfil_estruturado/domain/__init__.py`
- `src/jobsync/tests/perfil_estruturado/test_perfil_estruturado.py`

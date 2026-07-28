# Tarefa 1.0: Modelar domínio (PerfilEstruturado, DadosPerfilExtraidos, sub-entidades) + porta de repositório

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar as entidades de domínio do Perfil Estruturado: os value objects `ExperienciaProfissional`, `FormacaoAcademica`, `Certificacao`, `Idioma`/`NivelIdioma`, o agregado `PerfilEstruturado` e o "rascunho" `DadosPerfilExtraidos` (mesma forma, sem `perfil_identificador`), além da porta de repositório.

<requirements>
- `NivelIdioma`: enum com `BASICO`, `INTERMEDIARIO`, `AVANCADO`, `FLUENTE`, `NATIVO`.
- `ExperienciaProfissional`: dataclass frozen — `empresa`, `cargo`, `periodo` (texto livre), `descricao`. Validação: `empresa` e `cargo` não vazios.
- `FormacaoAcademica`: dataclass frozen — `instituicao`, `curso`, `periodo`. Validação: `instituicao` e `curso` não vazios.
- `Certificacao`: dataclass frozen — `nome`, `instituicao`, `ano`. Validação: `nome` não vazio.
- `Idioma`: dataclass frozen — `idioma: str`, `nivel: NivelIdioma`. Validação: `idioma` não vazio.
- `DadosPerfilExtraidos`: dataclass frozen — `nome_completo`, `email`, `linkedin`, `resumo_profissional`, `experiencias: tuple[ExperienciaProfissional, ...]`, `formacoes: tuple[FormacaoAcademica, ...]`, `certificacoes: tuple[Certificacao, ...]`, `idiomas: tuple[Idioma, ...]`, `tecnologias: tuple[str, ...]`. Sem validação obrigatória de nome/email (é um rascunho, pode vir incompleto da IA).
- `PerfilEstruturado`: mesma forma de `DadosPerfilExtraidos` mais `perfil_identificador: str` no início. Validação: `perfil_identificador`, `nome_completo` e `email` não vazios.
- `PerfilEstruturadoRepository` (ABC) em `src/domain/perfil_estruturado/perfil_estruturado_repository.py`: `salvar(perfil: PerfilEstruturado) -> PerfilEstruturado`, `buscar_por_perfil(perfil_identificador: str) -> PerfilEstruturado | None`.
- Complexidade: medium (várias entidades pequenas, mas nenhuma lógica complexa).
</requirements>

## Subtarefas

- [ ] 1.1 Criar `src/domain/perfil_estruturado/__init__.py` com `NivelIdioma`, `ExperienciaProfissional`, `FormacaoAcademica`, `Certificacao`, `Idioma`, `DadosPerfilExtraidos`, `PerfilEstruturado`.
- [ ] 1.2 Criar `src/domain/perfil_estruturado/perfil_estruturado_repository.py` com a porta `PerfilEstruturadoRepository`.
- [ ] 1.3 Escrever testes unitários das invariantes de cada entidade.

## Detalhes de Implementação

Consultar a seção "Modelos de Dados" de `techspec-job-0009.md`. Seguir o estilo já usado em `src/domain/candidatura/__init__.py` (múltiplas entidades no mesmo módulo) e `src/domain/curriculo_salvo/curriculo_salvo_repository.py` (porta de repositório).

## Critérios de Sucesso

- Todas as entidades são instanciáveis, imutáveis, e `PerfilEstruturado`/`ExperienciaProfissional`/`FormacaoAcademica`/`Certificacao`/`Idioma` validam seus campos obrigatórios.
- `DadosPerfilExtraidos` não exige `perfil_identificador` (não tem esse campo) nem valida nome/email como obrigatórios.

## Testes da Tarefa

- [ ] Teste unitário: `PerfilEstruturado` com `perfil_identificador`, `nome_completo` ou `email` vazios levanta `ValueError`.
- [ ] Teste unitário: `ExperienciaProfissional`/`FormacaoAcademica`/`Certificacao`/`Idioma` com campos obrigatórios vazios levantam `ValueError`.
- [ ] Teste unitário: `PerfilEstruturado` e `DadosPerfilExtraidos` válidos são instanciáveis com listas vazias de experiências/formações/certificações/idiomas/tecnologias.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/domain/perfil_estruturado/__init__.py`
- `src/domain/perfil_estruturado/perfil_estruturado_repository.py`
- `src/tests/domain/perfil_estruturado/__init__.py`
- `src/tests/domain/perfil_estruturado/test_perfil_estruturado.py`

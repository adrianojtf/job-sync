# Tarefa 1.0: Modelar entidades de domínio Perfil e CurriculoSalvo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar as duas novas entidades de domínio que servem de base para todo o restante da Fase 0: `Perfil` (usuário identificado por um identificador simples, sem senha) e `CurriculoSalvo` (PDF salvo na biblioteca de um perfil). Ambas seguem o mesmo padrão de dataclass imutável já usado em `domain/curriculo.py` e `domain/analise_vaga.py`.

<requirements>
- `Perfil` deve validar que `identificador` não é vazio.
- `CurriculoSalvo` deve validar que `nome_referencia` não é vazio e que `pdf_bytes` não é vazio.
- Nenhuma das duas entidades pode depender de infraestrutura (sem import de `sqlite3`, `streamlit`, etc.) — complexidade: low.
</requirements>

## Subtarefas

- [x] 1.1 Criar `domain/perfil.py` com o dataclass `Perfil` (`identificador: str`) e validação em `__post_init__`.
- [x] 1.2 Criar `domain/curriculo_salvo.py` com o dataclass `CurriculoSalvo` (`id`, `perfil_identificador`, `nome_referencia`, `pdf_bytes`, `data_upload`) e validação em `__post_init__`.
- [x] 1.3 Escrever testes unitários para as invariantes de ambas as entidades.

## Detalhes de Implementação

Consultar a seção "Modelos de Dados" de `techspec-job-0004.md` para os campos exatos de `Perfil` e `CurriculoSalvo`. Seguir o estilo de `domain/curriculo.py` (dataclass `frozen=True`, validação em `__post_init__` levantando `ValueError`).

## Critérios de Sucesso

- `Perfil` e `CurriculoSalvo` instanciáveis e imutáveis, com validação de campos obrigatórios.
- Nenhuma dependência de infraestrutura introduzida no domínio.

## Testes da Tarefa

- [x] Teste unitário: `Perfil` com identificador vazio levanta `ValueError`.
- [x] Teste unitário: `CurriculoSalvo` com `nome_referencia` vazio levanta `ValueError`.
- [x] Teste unitário: `CurriculoSalvo` com `pdf_bytes` vazio levanta `ValueError`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `domain/perfil.py`
- `domain/curriculo_salvo.py`
- `tests/domain/test_perfil.py`
- `tests/domain/test_curriculo_salvo.py`

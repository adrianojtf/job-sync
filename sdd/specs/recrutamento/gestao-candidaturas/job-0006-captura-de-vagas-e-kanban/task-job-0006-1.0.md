# Tarefa 1.0: Modelar entidades de domínio (Vaga, Candidatura, StatusCandidatura, TokenCaptura)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar as entidades de domínio da Fase 2: `Vaga` (capturada de uma página ou colada manualmente), `Candidatura` (com `StatusCandidatura` e histórico simplificado de mudança de status) e `TokenCaptura` (associação entre um token opaco e um perfil, usada pela extensão de navegador).

<requirements>
- `Vaga`: `id`, `perfil_identificador`, `texto_descricao`, `url_origem`, `data_captura`.
- `StatusCandidatura`: enum com `APLICADO`, `ENTREVISTA`, `OFERTA`, `REJEITADO`.
- `MudancaStatus`: value object simples com `status: StatusCandidatura` e `data: datetime` — representa apenas a mudança mais recente nesta fase (ver nota de implementação no resumo-tasks).
- `Candidatura`: `id`, `perfil_identificador`, `vaga_id`, `curriculo_salvo_id`, `empresa`, `cargo`, `status`, `data_aplicacao`, `historico_status: tuple[MudancaStatus, ...]`.
- `TokenCaptura`: `token: str`, `perfil_identificador: str`.
- Todas as entidades imutáveis (dataclass frozen), com validação de campos obrigatórios em `__post_init__` — complexidade: low.
</requirements>

## Subtarefas

- [x] 1.1 Criar `domain/vaga.py` com o dataclass `Vaga`.
- [x] 1.2 Criar `domain/candidatura.py` com `StatusCandidatura`, `MudancaStatus` e `Candidatura`.
- [x] 1.3 Criar `domain/token_captura.py` com o dataclass `TokenCaptura`.
- [x] 1.4 Escrever testes unitários para as invariantes das três entidades.

## Detalhes de Implementação

Consultar a seção "Modelos de Dados" de `techspec-job-0006.md`. Seguir o estilo já usado em `domain/perfil.py` e `domain/curriculo_salvo.py` (Fase 0).

## Critérios de Sucesso

- As quatro entidades/tipos (`Vaga`, `StatusCandidatura`, `Candidatura`, `TokenCaptura`) são instanciáveis, imutáveis e validam campos obrigatórios.

## Testes da Tarefa

- [x] Teste unitário: `Vaga` com `texto_descricao` vazio levanta `ValueError`.
- [x] Teste unitário: `Candidatura` com `empresa` ou `cargo` vazio levanta `ValueError`.
- [x] Teste unitário: `TokenCaptura` com `token` vazio levanta `ValueError`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `domain/vaga.py`
- `domain/candidatura.py`
- `domain/token_captura.py`
- `tests/domain/test_vaga.py`
- `tests/domain/test_candidatura.py`
- `tests/domain/test_token_captura.py`

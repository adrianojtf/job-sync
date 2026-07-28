# Tarefa 9.0: Adicionar data_publicacao em VagaExterna + parsing de data em cada adapter

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Adicionar o campo `data_publicacao: date | None` a `VagaExterna` e popular esse campo em cada um dos cinco adapters a partir do campo de data específico da fonte, quando existir.

<requirements>
- `VagaExterna.data_publicacao: date | None = None` (novo campo, default `None` para não quebrar construtores existentes).
- `BuscadorRemoteOk`: parseia `date` (string ISO 8601) via `datetime.fromisoformat(...).date()`; se ausente ou inválido, `data_publicacao=None`.
- `BuscadorWeWorkRemotely`: usa `entry.published_parsed` (struct_time do feedparser) convertido para `date`; se ausente, `None`.
- `BuscadorArbeitnow`: parseia `created_at` (timestamp Unix) via `datetime.fromtimestamp(...).date()`; se ausente, `None`.
- `BuscadorAdzuna`: parseia `created` (string ISO 8601); se ausente, `None`.
- `BuscadorGoogleCustomSearch`: sempre `data_publicacao=None` — a API não expõe data de publicação da vaga, só de indexação da página, e não se deve confundir as duas (ver PRD/TechSpec).
- Falha ao parsear (formato inesperado) deve resultar em `None`, nunca lançar exceção — mesma filosofia de resiliência já usada nos adapters (nunca propagar exceção não tratada).
- Complexidade: medium (cinco parsings de data diferentes, cada um com seu formato).
</requirements>

## Subtarefas

- [ ] 9.1 Adicionar `data_publicacao` a `VagaExterna` em `src/domain/vaga_externa/__init__.py`.
- [ ] 9.2 Implementar parsing de data em `BuscadorRemoteOk`, com teste.
- [ ] 9.3 Implementar parsing de data em `BuscadorWeWorkRemotely`, com teste.
- [ ] 9.4 Implementar parsing de data em `BuscadorArbeitnow`, com teste.
- [ ] 9.5 Implementar parsing de data em `BuscadorAdzuna`, com teste.
- [ ] 9.6 Confirmar (com teste) que `BuscadorGoogleCustomSearch` sempre retorna `data_publicacao=None`.
- [ ] 9.7 Teste de cada adapter cobrindo o caso de data ausente/malformada retornando `None` sem exceção.

## Detalhes de Implementação

Consultar a seção "Pontos de Integração" (atualizada com o campo de data por fonte) de `techspec-job-0007.md`.

## Critérios de Sucesso

- Todos os cinco adapters populam (ou deixam `None` de forma segura) `data_publicacao` sem lançar exceção em nenhum cenário.

## Testes da Tarefa

- [ ] Teste unitário por adapter (exceto Google): data válida mapeada corretamente para `data_publicacao`.
- [ ] Teste unitário por adapter (exceto Google): data ausente/malformada resulta em `data_publicacao=None`, sem exceção.
- [ ] Teste unitário: `BuscadorGoogleCustomSearch` sempre retorna `data_publicacao=None`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/domain/vaga_externa/__init__.py`
- `src/infrastructure/fontes_vagas/buscador_remoteok.py`
- `src/infrastructure/fontes_vagas/buscador_wwr.py`
- `src/infrastructure/fontes_vagas/buscador_arbeitnow.py`
- `src/infrastructure/fontes_vagas/buscador_adzuna.py`
- `src/infrastructure/fontes_vagas/buscador_google_custom_search.py`
- `src/tests/domain/vaga_externa/test_vaga_externa.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_remoteok.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_wwr.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_arbeitnow.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_adzuna.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_google_custom_search.py`

# Tarefa 2.0: Definir BuscadorVagasExternoPort + adapters de API direta (RemoteOK, We Work Remotely, Arbeitnow, Adzuna)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Definir a porta única `BuscadorVagasExternoPort` e implementar os quatro adapters de fontes que têm API de busca direta (sem a etapa extra de extração de página que o Google Custom Search exige, tratada na Tarefa 3.0).

<requirements>
- `BuscadorVagasExternoPort` (ABC) em `src/domain/vaga_externa/buscador_vagas_externo_port.py`: método `buscar(self, termo: str) -> tuple[VagaExterna, ...]`.
- `BuscadorRemoteOk`: `GET https://remoteok.com/api?search={termo}`, sem autenticação.
- `BuscadorWeWorkRemotely`: consome o feed RSS público, faz parsing de XML (`feedparser`) e filtra localmente pelo termo (a fonte não suporta busca por query string nativamente).
- `BuscadorArbeitnow`: `GET https://www.arbeitnow.com/api/job-board-api?search={termo}`, sem autenticação.
- `BuscadorAdzuna`: `GET https://api.adzuna.com/v1/api/jobs/{pais}/search/1?app_id={id}&app_key={key}&what={termo}`, credenciais via `ADZUNA_APP_ID`/`ADZUNA_APP_KEY` no `.env`.
- Cada adapter deve capturar exceções de rede/timeout e traduzi-las para `TimeoutError`, ou retornar tupla vazia — nunca propagar exceção não tratada.
- Complexidade: medium (quatro integrações HTTP distintas, cada uma com formato de resposta próprio).
</requirements>

## Subtarefas

- [ ] 2.1 Criar `src/domain/vaga_externa/buscador_vagas_externo_port.py` com a porta `BuscadorVagasExternoPort`.
- [ ] 2.2 Implementar `src/infrastructure/fontes_vagas/buscador_remoteok.py`, com teste usando fixture JSON de exemplo.
- [ ] 2.3 Implementar `src/infrastructure/fontes_vagas/buscador_wwr.py`, com teste usando fixture RSS/XML de exemplo.
- [ ] 2.4 Implementar `src/infrastructure/fontes_vagas/buscador_arbeitnow.py`, com teste usando fixture JSON de exemplo.
- [ ] 2.5 Implementar `src/infrastructure/fontes_vagas/buscador_adzuna.py`, com teste usando fixture JSON de exemplo.
- [ ] 2.6 Escrever testes de tratamento de erro/timeout para os quatro adapters.

## Detalhes de Implementação

Consultar as seções "Interfaces Principais" e "Pontos de Integração" de `techspec-job-0007.md`. Adicionar `httpx` e `feedparser` a `requirements.txt`.

## Critérios de Sucesso

- Os quatro adapters implementam `BuscadorVagasExternoPort` e convertem corretamente a resposta de cada fonte para `tuple[VagaExterna, ...]`.
- Falha de rede/timeout em qualquer adapter não propaga exceção não tratada.

## Testes da Tarefa

- [ ] Teste unitário por adapter: resposta HTTP mockada mapeada corretamente para `VagaExterna`.
- [ ] Teste unitário por adapter: timeout/erro de rede tratado sem exceção não capturada.
- [ ] Teste unitário: `BuscadorWeWorkRemotely` filtra corretamente pelo termo no feed RSS.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/domain/vaga_externa/buscador_vagas_externo_port.py`
- `src/infrastructure/fontes_vagas/buscador_remoteok.py`
- `src/infrastructure/fontes_vagas/buscador_wwr.py`
- `src/infrastructure/fontes_vagas/buscador_arbeitnow.py`
- `src/infrastructure/fontes_vagas/buscador_adzuna.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_remoteok.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_wwr.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_arbeitnow.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_adzuna.py`
- `requirements.txt`

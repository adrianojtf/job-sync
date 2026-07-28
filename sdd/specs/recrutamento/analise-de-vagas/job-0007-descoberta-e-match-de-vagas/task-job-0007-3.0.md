# Tarefa 3.0: Definir ExtratorTextoPaginaPort + adapter BuscadorGoogleCustomSearch

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar a quinta fonte de busca, Google Custom Search, que difere das demais por só devolver link+snippet: é preciso buscar a página de origem e extrair o texto principal para produzir uma descrição comparável às outras fontes, com fallback gracioso quando isso não é possível.

<requirements>
- `ExtratorTextoPaginaPort` (ABC) em `src/domain/vaga_externa/extrator_texto_pagina_port.py`: método `extrair(self, url: str) -> str | None` (retorna `None` se a extração falhar).
- `BuscadorGoogleCustomSearch`: `GET https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={termo}`, credenciais via `GOOGLE_CSE_API_KEY`/`GOOGLE_CSE_ID` no `.env`.
- Para cada resultado, tenta extrair a descrição completa via `ExtratorTextoPaginaPort`; se falhar, usa o snippet retornado pela busca e marca `descricao_incompleta=True`.
- HTTP 429 (cota diária de 100 buscas esgotada) deve ser tratado especificamente, retornando tupla vazia com log de warning, sem propagar erro.
- Complexidade: medium (integração com duas chamadas HTTP em sequência + tratamento de cota).
</requirements>

## Subtarefas

- [ ] 3.1 Criar `src/domain/vaga_externa/extrator_texto_pagina_port.py` com a porta `ExtratorTextoPaginaPort`.
- [ ] 3.2 Implementar `src/infrastructure/fontes_vagas/extrator_texto_pagina.py` (httpx + BeautifulSoup, heurística genérica equivalente à de `content.js` da extensão).
- [ ] 3.3 Implementar `src/infrastructure/fontes_vagas/buscador_google_custom_search.py`.
- [ ] 3.4 Escrever testes: extração bem-sucedida, fallback para snippet, tratamento de HTTP 429.

## Detalhes de Implementação

Consultar as seções "Interfaces Principais" e "Pontos de Integração" de `techspec-job-0007.md`. Adicionar `beautifulsoup4` a `requirements.txt`.

## Critérios de Sucesso

- `BuscadorGoogleCustomSearch` retorna `VagaExterna` com descrição completa quando a extração da página funciona, e com o snippet + `descricao_incompleta=True` quando não funciona.
- Cota esgotada (HTTP 429) não derruba a busca; retorna tupla vazia com log de warning.

## Testes da Tarefa

- [ ] Teste unitário: extração bem-sucedida da página de origem produz `descricao_incompleta=False`.
- [ ] Teste unitário: falha na extração (ex: página bloqueia acesso) cai para snippet com `descricao_incompleta=True`.
- [ ] Teste unitário: resposta HTTP 429 da API retorna tupla vazia sem exceção.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/domain/vaga_externa/extrator_texto_pagina_port.py`
- `src/infrastructure/fontes_vagas/extrator_texto_pagina.py`
- `src/infrastructure/fontes_vagas/buscador_google_custom_search.py`
- `src/tests/infrastructure/fontes_vagas/test_extrator_texto_pagina.py`
- `src/tests/infrastructure/fontes_vagas/test_buscador_google_custom_search.py`
- `requirements.txt`

"""Testes do adapter BuscadorGoogleCustomSearch, com resposta HTTP mockada."""

import httpx

from domain.vaga_externa import FonteVagaExterna
from infrastructure.fontes_vagas.buscador_google_custom_search import BuscadorGoogleCustomSearch

_REQUEST_FAKE = httpx.Request("GET", "https://www.googleapis.com/customsearch/v1")

_FIXTURE_BUSCA = {
    "items": [
        {
            "title": "Engenheiro de Software Backend - Gupy",
            "link": "https://gupy.io/vaga/1",
            "snippet": "Vaga na Gupy para engenheiro backend...",
            "displayLink": "gupy.io",
        }
    ]
}


class _ExtratorFake:
    def __init__(self, texto: str | None) -> None:
        self._texto = texto

    def extrair(self, url: str) -> str | None:
        return self._texto


class TestBuscadorGoogleCustomSearch:
    def test_extracao_bem_sucedida_usa_descricao_completa(self, monkeypatch):
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, json=_FIXTURE_BUSCA, request=_REQUEST_FAKE)
        )
        buscador = BuscadorGoogleCustomSearch(
            api_key="key", search_engine_id="cx", extrator_texto_pagina=_ExtratorFake("Descrição completa da vaga.")
        )

        vagas = buscador.buscar("backend")

        assert len(vagas) == 1
        assert vagas[0].descricao == "Descrição completa da vaga."
        assert vagas[0].descricao_incompleta is False
        assert vagas[0].fonte == FonteVagaExterna.GOOGLE_CUSTOM_SEARCH
        assert vagas[0].data_publicacao is None

    def test_falha_na_extracao_cai_para_snippet(self, monkeypatch):
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, json=_FIXTURE_BUSCA, request=_REQUEST_FAKE)
        )
        buscador = BuscadorGoogleCustomSearch(
            api_key="key", search_engine_id="cx", extrator_texto_pagina=_ExtratorFake(None)
        )

        vagas = buscador.buscar("backend")

        assert len(vagas) == 1
        assert vagas[0].descricao == "Vaga na Gupy para engenheiro backend..."
        assert vagas[0].descricao_incompleta is True

    def test_http_429_cota_esgotada_retorna_tupla_vazia(self, monkeypatch):
        monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(429, request=_REQUEST_FAKE))
        buscador = BuscadorGoogleCustomSearch(
            api_key="key", search_engine_id="cx", extrator_texto_pagina=_ExtratorFake(None)
        )

        assert buscador.buscar("backend") == ()

    def test_erro_de_rede_retorna_tupla_vazia(self, monkeypatch):
        def levantar_erro(*args, **kwargs):
            raise httpx.ConnectTimeout("timeout")

        monkeypatch.setattr(httpx, "get", levantar_erro)
        buscador = BuscadorGoogleCustomSearch(
            api_key="key", search_engine_id="cx", extrator_texto_pagina=_ExtratorFake(None)
        )

        assert buscador.buscar("backend") == ()

"""Testes dos adapters de buscadores de vagas externas, com HTTP mockado."""

from datetime import date
from types import SimpleNamespace

import httpx
import pytest

from jobsync.vaga_externa import FonteVagaExterna
from jobsync.vaga_externa.adapters import (
    BuscadorAdzunaClient,
    BuscadorArbeitnowClient,
    BuscadorGoogleCustomSearchClient,
    BuscadorRemoteOkClient,
    BuscadorWeWorkRemotelyClient,
)
from jobsync.vaga_externa.domain.extrator_texto_pagina_port import ExtratorTextoPaginaPort

_REQUEST_FAKE = httpx.Request("GET", "https://api.example.com/jobs")


class ExtratorTextoPaginaFake(ExtratorTextoPaginaPort):
    def __init__(self, texto_por_url: dict[str, str | None]):
        self._texto_por_url = texto_por_url

    def extrair(self, url: str) -> str | None:
        return self._texto_por_url.get(url)


def test_buscador_adzuna_mapeia_resposta_para_vaga_externa(monkeypatch):
    fixture = {
        "results": [
            {
                "title": "Engenheiro de Software Backend",
                "company": {"display_name": "TechCorp"},
                "description": "Vaga remota para engenheiro backend com Python.",
                "redirect_url": "https://adzuna.com/jobs/1",
                "created": "2026-07-20T10:00:00Z",
            }
        ]
    }
    monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(200, json=fixture, request=_REQUEST_FAKE))

    vagas = BuscadorAdzunaClient(app_id="id", app_key="key").buscar("backend")

    assert len(vagas) == 1
    assert vagas[0].titulo == "Engenheiro de Software Backend"
    assert vagas[0].empresa == "TechCorp"
    assert vagas[0].fonte == FonteVagaExterna.ADZUNA
    assert vagas[0].data_publicacao == date(2026, 7, 20)


def test_buscador_adzuna_repassa_max_days_old(monkeypatch):
    fixture = {"results": []}
    chamadas = []

    def capturar(*args, **kwargs):
        chamadas.append(kwargs.get("params", {}))
        return httpx.Response(200, json=fixture, request=_REQUEST_FAKE)

    monkeypatch.setattr(httpx, "get", capturar)

    BuscadorAdzunaClient(app_id="id", app_key="key").buscar("backend", dias_maximo=7)

    assert chamadas[0]["max_days_old"] == 7


def test_buscador_adzuna_erro_de_rede_retorna_vazio(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectTimeout("timeout")))

    assert BuscadorAdzunaClient(app_id="id", app_key="key").buscar("backend") == ()


def test_buscador_arbeitnow_mapeia_resposta(monkeypatch):
    fixture = {
        "data": [
            {
                "title": "Backend Engineer",
                "company_name": " Startup ",
                "description": "Python role",
                "url": "https://arbeitnow.com/1",
                "created_at": 1752931200,
            }
        ]
    }
    monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(200, json=fixture, request=_REQUEST_FAKE))

    vagas = BuscadorArbeitnowClient().buscar("python")

    assert len(vagas) == 1
    assert vagas[0].titulo == "Backend Engineer"
    assert vagas[0].fonte == FonteVagaExterna.ARBEITNOW
    assert vagas[0].data_publicacao == date(2025, 7, 19)


def test_buscador_arbeitnow_erro_de_rede_retorna_vazio(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectError("erro")))

    assert BuscadorArbeitnowClient().buscar("python") == ()


def test_buscador_remoteok_mapeia_resposta(monkeypatch):
    fixture = [
        {
            "position": "Fullstack Developer",
            "company": "RemoteCo",
            "description": "React + Python",
            "url": "https://remoteok.com/1",
            "date": "2026-07-20T10:00:00Z",
        }
    ]
    monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(200, json=fixture, request=_REQUEST_FAKE))

    vagas = BuscadorRemoteOkClient().buscar("fullstack")

    assert len(vagas) == 1
    assert vagas[0].titulo == "Fullstack Developer"
    assert vagas[0].fonte == FonteVagaExterna.REMOTEOK


def test_buscador_remoteok_erro_de_rede_retorna_vazio(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: (_ for _ in ()).throw(httpx.ReadTimeout("timeout")))

    assert BuscadorRemoteOkClient().buscar("fullstack") == ()


def test_buscador_google_custom_search_usa_extrator_e_snippet(monkeypatch):
    fixture = {
        "items": [
            {
                "title": "Vaga Google",
                "displayLink": "example.com",
                "link": "https://example.com/job/1",
                "snippet": "snippet da vaga",
            }
        ]
    }
    extrator = ExtratorTextoPaginaFake({"https://example.com/job/1": "descrição completa da vaga"})
    monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(200, json=fixture, request=_REQUEST_FAKE))

    vagas = BuscadorGoogleCustomSearchClient(
        api_key="key",
        search_engine_id="cx",
        extrator_texto_pagina=extrator,
    ).buscar("engenheiro")

    assert len(vagas) == 1
    assert vagas[0].titulo == "Vaga Google"
    assert vagas[0].descricao == "descrição completa da vaga"
    assert vagas[0].descricao_incompleta is False
    assert vagas[0].fonte == FonteVagaExterna.GOOGLE_CUSTOM_SEARCH


def test_buscador_google_custom_search_cai_para_snippet_quando_extrator_falha(monkeypatch):
    fixture = {
        "items": [
            {
                "title": "Vaga Google",
                "link": "https://example.com/job/1",
                "snippet": "fallback snippet",
            }
        ]
    }
    extrator = ExtratorTextoPaginaFake({"https://example.com/job/1": None})
    monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(200, json=fixture, request=_REQUEST_FAKE))

    vagas = BuscadorGoogleCustomSearchClient(
        api_key="key",
        search_engine_id="cx",
        extrator_texto_pagina=extrator,
    ).buscar("engenheiro")

    assert len(vagas) == 1
    assert vagas[0].descricao == "fallback snippet"
    assert vagas[0].descricao_incompleta is True


def test_buscador_google_custom_search_cota_esgotada_retorna_vazio(monkeypatch):
    def fake_get(*a, **k):
        return httpx.Response(429, request=_REQUEST_FAKE)

    extrator = ExtratorTextoPaginaFake({})
    monkeypatch.setattr(httpx, "get", fake_get)

    vagas = BuscadorGoogleCustomSearchClient(
        api_key="key",
        search_engine_id="cx",
        extrator_texto_pagina=extrator,
    ).buscar("engenheiro")

    assert vagas == ()


def test_buscador_wwr_filtra_por_termo_e_mapeia_feed(monkeypatch):
    import feedparser
    from jobsync.vaga_externa.adapters import buscador_wwr_client as wwr_mod

    def fake_get(*a, **k):
        return httpx.Response(200, content=b"<rss/>", request=_REQUEST_FAKE)

    def fake_parse(conteudo):
        return SimpleNamespace(
            entries=[
                SimpleNamespace(
                    title="TechCorp: Backend Engineer",
                    summary="Vaga remota com Python",
                    link="https://weworkremotely.com/1",
                    published_parsed=(2026, 7, 20, 10, 0, 0),
                ),
                SimpleNamespace(
                    title="OutraEmpresa: Designer",
                    summary="Design role",
                    link="https://weworkremotely.com/2",
                    published_parsed=(2026, 7, 19, 10, 0, 0),
                ),
            ]
        )

    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(wwr_mod.feedparser, "parse", fake_parse)

    vagas = BuscadorWeWorkRemotelyClient().buscar("python")

    assert len(vagas) == 1
    assert vagas[0].titulo == "Backend Engineer"
    assert vagas[0].empresa == "TechCorp"
    assert vagas[0].fonte == FonteVagaExterna.WE_WORK_REMOTELY
    assert vagas[0].data_publicacao == date(2026, 7, 20)

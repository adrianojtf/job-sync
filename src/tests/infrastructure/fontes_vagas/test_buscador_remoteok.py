"""Testes do adapter BuscadorRemoteOk, com resposta HTTP mockada."""

from datetime import date

import httpx
import pytest

from domain.vaga_externa import FonteVagaExterna
from infrastructure.fontes_vagas.buscador_remoteok import BuscadorRemoteOk

_REQUEST_FAKE = httpx.Request("GET", "https://remoteok.com/api")


class TestBuscadorRemoteOk:
    def test_mapeia_resposta_para_vaga_externa(self, monkeypatch):
        fixture = [
            {"legal": "aviso legal, não é uma vaga"},
            {
                "position": "Engenheiro de Software Backend",
                "company": "TechCorp",
                "description": "Vaga remota para engenheiro backend com Python.",
                "url": "https://remoteok.com/remote-jobs/123",
                "date": "2026-07-20T00:00:00+00:00",
            },
        ]
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, json=fixture, request=_REQUEST_FAKE)
        )

        vagas = BuscadorRemoteOk().buscar("backend")

        assert len(vagas) == 1
        assert vagas[0].titulo == "Engenheiro de Software Backend"
        assert vagas[0].fonte == FonteVagaExterna.REMOTEOK
        assert vagas[0].data_publicacao == date(2026, 7, 20)

    def test_data_ausente_ou_invalida_resulta_em_none(self, monkeypatch):
        fixture = [
            {"position": "Vaga sem data", "company": "TechCorp", "url": "https://remoteok.com/x"},
            {"position": "Vaga com data invalida", "company": "TechCorp", "url": "https://remoteok.com/y", "date": "nao-e-uma-data"},
        ]
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, json=fixture, request=_REQUEST_FAKE)
        )

        vagas = BuscadorRemoteOk().buscar("backend")

        assert all(v.data_publicacao is None for v in vagas)

    def test_erro_de_rede_retorna_tupla_vazia(self, monkeypatch):
        def levantar_erro(*args, **kwargs):
            raise httpx.ConnectTimeout("timeout")

        monkeypatch.setattr(httpx, "get", levantar_erro)

        assert BuscadorRemoteOk().buscar("backend") == ()

    def test_http_500_retorna_tupla_vazia(self, monkeypatch):
        monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(500, request=_REQUEST_FAKE))

        assert BuscadorRemoteOk().buscar("backend") == ()

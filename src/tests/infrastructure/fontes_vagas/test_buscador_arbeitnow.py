"""Testes do adapter BuscadorArbeitnow, com resposta HTTP mockada."""

from datetime import date, datetime, timezone

import httpx

from domain.vaga_externa import FonteVagaExterna
from infrastructure.fontes_vagas.buscador_arbeitnow import BuscadorArbeitnow

_REQUEST_FAKE = httpx.Request("GET", "https://www.arbeitnow.com/api/job-board-api")


class TestBuscadorArbeitnow:
    def test_mapeia_resposta_para_vaga_externa(self, monkeypatch):
        timestamp = int(datetime(2026, 7, 20, tzinfo=timezone.utc).timestamp())
        fixture = {
            "data": [
                {
                    "title": "Engenheiro de Software Backend",
                    "company_name": "TechCorp",
                    "description": "Vaga remota para engenheiro backend com Python.",
                    "url": "https://arbeitnow.com/jobs/1",
                    "created_at": timestamp,
                }
            ]
        }
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, json=fixture, request=_REQUEST_FAKE)
        )

        vagas = BuscadorArbeitnow().buscar("backend")

        assert len(vagas) == 1
        assert vagas[0].titulo == "Engenheiro de Software Backend"
        assert vagas[0].empresa == "TechCorp"
        assert vagas[0].fonte == FonteVagaExterna.ARBEITNOW
        assert vagas[0].data_publicacao == date(2026, 7, 20)

    def test_data_ausente_resulta_em_none(self, monkeypatch):
        fixture = {"data": [{"title": "Vaga sem data", "company_name": "TechCorp", "url": "https://x"}]}
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, json=fixture, request=_REQUEST_FAKE)
        )

        vagas = BuscadorArbeitnow().buscar("backend")

        assert vagas[0].data_publicacao is None

    def test_erro_de_rede_retorna_tupla_vazia(self, monkeypatch):
        def levantar_erro(*args, **kwargs):
            raise httpx.ConnectTimeout("timeout")

        monkeypatch.setattr(httpx, "get", levantar_erro)

        assert BuscadorArbeitnow().buscar("backend") == ()

    def test_http_500_retorna_tupla_vazia(self, monkeypatch):
        monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(500, request=_REQUEST_FAKE))

        assert BuscadorArbeitnow().buscar("backend") == ()

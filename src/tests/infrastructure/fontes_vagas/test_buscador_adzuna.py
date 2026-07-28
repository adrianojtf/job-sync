"""Testes do adapter BuscadorAdzuna, com resposta HTTP mockada."""

from datetime import date

import httpx

from domain.vaga_externa import FonteVagaExterna
from infrastructure.fontes_vagas.buscador_adzuna import BuscadorAdzuna

_REQUEST_FAKE = httpx.Request("GET", "https://api.adzuna.com/v1/api/jobs/gb/search/1")

_FIXTURE = {
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


class TestBuscadorAdzuna:
    def test_mapeia_resposta_para_vaga_externa(self, monkeypatch):
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, json=_FIXTURE, request=_REQUEST_FAKE)
        )

        vagas = BuscadorAdzuna(app_id="id", app_key="key").buscar("backend")

        assert len(vagas) == 1
        assert vagas[0].titulo == "Engenheiro de Software Backend"
        assert vagas[0].empresa == "TechCorp"
        assert vagas[0].fonte == FonteVagaExterna.ADZUNA
        assert vagas[0].data_publicacao == date(2026, 7, 20)

    def test_dias_maximo_e_repassado_como_max_days_old(self, monkeypatch):
        chamadas = []

        def capturar(*args, **kwargs):
            chamadas.append(kwargs.get("params", {}))
            return httpx.Response(200, json=_FIXTURE, request=_REQUEST_FAKE)

        monkeypatch.setattr(httpx, "get", capturar)

        BuscadorAdzuna(app_id="id", app_key="key").buscar("backend", dias_maximo=7)

        assert chamadas[0]["max_days_old"] == 7

    def test_sem_dias_maximo_nao_inclui_max_days_old(self, monkeypatch):
        chamadas = []

        def capturar(*args, **kwargs):
            chamadas.append(kwargs.get("params", {}))
            return httpx.Response(200, json=_FIXTURE, request=_REQUEST_FAKE)

        monkeypatch.setattr(httpx, "get", capturar)

        BuscadorAdzuna(app_id="id", app_key="key").buscar("backend")

        assert "max_days_old" not in chamadas[0]

    def test_erro_de_rede_retorna_tupla_vazia(self, monkeypatch):
        def levantar_erro(*args, **kwargs):
            raise httpx.ConnectTimeout("timeout")

        monkeypatch.setattr(httpx, "get", levantar_erro)

        assert BuscadorAdzuna(app_id="id", app_key="key").buscar("backend") == ()

    def test_http_401_credenciais_invalidas_retorna_tupla_vazia(self, monkeypatch):
        monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(401, request=_REQUEST_FAKE))

        assert BuscadorAdzuna(app_id="id", app_key="key").buscar("backend") == ()

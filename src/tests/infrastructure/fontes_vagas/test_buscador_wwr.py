"""Testes do adapter BuscadorWeWorkRemotely, com feed RSS mockado."""

from datetime import date

import httpx

from domain.vaga_externa import FonteVagaExterna
from infrastructure.fontes_vagas.buscador_wwr import BuscadorWeWorkRemotely

_REQUEST_FAKE = httpx.Request("GET", "https://weworkremotely.com/categories/remote-programming-jobs.rss")

_FEED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>We Work Remotely</title>
<item>
<title>TechCorp: Engenheiro de Software Backend</title>
<link>https://weworkremotely.com/remote-jobs/1</link>
<description>Vaga remota para engenheiro backend com Python.</description>
<pubDate>Mon, 20 Jul 2026 00:00:00 +0000</pubDate>
</item>
<item>
<title>OutraEmpresa: Designer Grafico</title>
<link>https://weworkremotely.com/remote-jobs/2</link>
<description>Vaga remota para designer.</description>
</item>
</channel>
</rss>""".encode("utf-8")


class TestBuscadorWeWorkRemotely:
    def test_filtra_pelo_termo_no_titulo(self, monkeypatch):
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, content=_FEED_XML, request=_REQUEST_FAKE)
        )

        vagas = BuscadorWeWorkRemotely().buscar("backend")

        assert len(vagas) == 1
        assert vagas[0].titulo == "Engenheiro de Software Backend"
        assert vagas[0].empresa == "TechCorp"
        assert vagas[0].fonte == FonteVagaExterna.WE_WORK_REMOTELY
        assert vagas[0].data_publicacao == date(2026, 7, 20)

    def test_data_ausente_resulta_em_none(self, monkeypatch):
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, content=_FEED_XML, request=_REQUEST_FAKE)
        )

        vagas = BuscadorWeWorkRemotely().buscar("designer")

        assert len(vagas) == 1
        assert vagas[0].data_publicacao is None

    def test_termo_sem_correspondencia_retorna_vazio(self, monkeypatch):
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, content=_FEED_XML, request=_REQUEST_FAKE)
        )

        assert BuscadorWeWorkRemotely().buscar("inexistente-xyz") == ()

    def test_erro_de_rede_retorna_tupla_vazia(self, monkeypatch):
        def levantar_erro(*args, **kwargs):
            raise httpx.ConnectTimeout("timeout")

        monkeypatch.setattr(httpx, "get", levantar_erro)

        assert BuscadorWeWorkRemotely().buscar("backend") == ()

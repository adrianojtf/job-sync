"""Testes do destino seguro pós-login."""

import pytest

from jobsync.autenticacao.domain.destino import destino_seguro


class TestDestinoSeguro:
    @pytest.mark.parametrize("destino", ["/", "/vagas", "/candidaturas?aba=ativas", "/a/b#secao"])
    def test_mantem_caminhos_internos(self, destino):
        assert destino_seguro(destino) == destino

    @pytest.mark.parametrize(
        "destino",
        [
            None,
            "",
            "vagas",
            "//evil.com",
            "///evil.com",
            "/\\evil.com",
            "http://evil.com",
            "https://evil.com/x",
            "javascript:alert(1)",
            "/ok\nSet-Cookie: x=1",
            "/ok\r\nLocation: http://evil.com",
            "/ok\tx",
            "/" + "a" * 2100,
        ],
    )
    def test_destinos_perigosos_viram_raiz(self, destino):
        assert destino_seguro(destino) == "/"

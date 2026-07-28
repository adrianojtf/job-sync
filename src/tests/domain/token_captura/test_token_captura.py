"""Testes da entidade de domínio TokenCaptura."""

import pytest

from domain.token_captura import TokenCaptura


class TestTokenCaptura:
    def test_cria_token_captura_valido(self):
        token = TokenCaptura(token="abc123", perfil_identificador="matheus")

        assert token.token == "abc123"
        assert token.perfil_identificador == "matheus"

    def test_token_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            TokenCaptura(token="", perfil_identificador="matheus")

    def test_perfil_identificador_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            TokenCaptura(token="abc123", perfil_identificador="")

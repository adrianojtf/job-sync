"""Testes de integração do TokenCapturaRepositoryImpl."""


import pytest

from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl
from jobsync.token_captura.adapters import TokenCapturaRepositoryImpl


@pytest.fixture
def repositorio(pool_postgres):
    PerfilRepositoryImpl(pool_postgres).criar("matheus")
    return TokenCapturaRepositoryImpl(pool_postgres)


class TestTokenCapturaRepositoryImpl:
    def test_criar_token_captura_e_resolver_perfil(self, repositorio):
        token = repositorio.criar("matheus")

        assert repositorio.resolver_perfil_por_token(token.token) == "matheus"

    def test_resolver_perfil_com_token_inexistente_retorna_none(self, repositorio):
        assert repositorio.resolver_perfil_por_token("token-que-nao-existe") is None

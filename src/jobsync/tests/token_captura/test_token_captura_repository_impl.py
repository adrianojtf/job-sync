"""Testes de integração do TokenCapturaRepositoryImpl."""

import os
import tempfile

import pytest

from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl
from jobsync.token_captura.adapters import TokenCapturaRepositoryImpl


@pytest.fixture
def caminho_banco():
    fd, caminho = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield caminho
    os.remove(caminho)


@pytest.fixture
def repositorio(caminho_banco):
    PerfilRepositoryImpl(caminho_banco=caminho_banco).criar("matheus")
    return TokenCapturaRepositoryImpl(caminho_banco=caminho_banco)


class TestTokenCapturaRepositoryImpl:
    def test_criar_token_captura_e_resolver_perfil(self, repositorio):
        token = repositorio.criar("matheus")

        assert repositorio.resolver_perfil_por_token(token.token) == "matheus"

    def test_resolver_perfil_com_token_inexistente_retorna_none(self, repositorio):
        assert repositorio.resolver_perfil_por_token("token-que-nao-existe") is None

"""Testes de integração do PerfilRepositoryImpl."""

import os
import tempfile

import pytest

from infrastructure.persistence.perfil_repository_impl import PerfilRepositoryImpl


@pytest.fixture
def repositorio():
    fd, caminho = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    repo = PerfilRepositoryImpl(caminho_banco=caminho)
    yield repo
    os.remove(caminho)


class TestPerfilRepositoryImpl:
    def test_buscar_por_identificador_inexistente_retorna_none(self, repositorio):
        assert repositorio.buscar_por_identificador("matheus") is None

    def test_criar_persiste_e_permite_buscar_depois(self, repositorio):
        criado = repositorio.criar("matheus")

        encontrado = repositorio.buscar_por_identificador("matheus")

        assert encontrado == criado
        assert encontrado.identificador == "matheus"

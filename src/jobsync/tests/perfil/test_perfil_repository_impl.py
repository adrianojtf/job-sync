"""Testes de integração do PerfilRepositoryImpl."""

import pytest

from jobsync.perfil.adapters import PerfilRepositoryImpl


@pytest.fixture
def repositorio(pool_postgres):
    return PerfilRepositoryImpl(pool_postgres)


class TestPerfilRepositoryImpl:
    def test_buscar_por_identificador_inexistente_retorna_none(self, repositorio):
        assert repositorio.buscar_por_identificador("matheus") is None

    def test_criar_persiste_e_permite_buscar_depois(self, repositorio):
        criado = repositorio.criar("matheus")

        encontrado = repositorio.buscar_por_identificador("matheus")

        assert encontrado == criado
        assert encontrado.identificador == "matheus"

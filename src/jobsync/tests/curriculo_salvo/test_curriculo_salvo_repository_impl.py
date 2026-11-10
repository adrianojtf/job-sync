"""Testes de integração do CurriculoSalvoRepositoryImpl."""

from datetime import datetime, timezone

import pytest

from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl
from jobsync.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.adapters import CurriculoSalvoRepositoryImpl


@pytest.fixture
def repositorio(pool_postgres):
    PerfilRepositoryImpl(pool_postgres).criar("matheus")
    PerfilRepositoryImpl(pool_postgres).criar("outra-pessoa")
    return CurriculoSalvoRepositoryImpl(pool_postgres)


def _criar_curriculo_salvo(**overrides) -> CurriculoSalvo:
    dados = dict(
        id="uuid-1",
        perfil_identificador="matheus",
        nome_referencia="Currículo Backend",
        pdf_bytes=b"%PDF-fake",
        data_upload=datetime(2026, 7, 26, 10, 0, 0, tzinfo=timezone.utc),
    )
    dados.update(overrides)
    return CurriculoSalvo(**dados)


class TestCurriculoSalvoRepositoryImpl:
    def test_salvar_e_listar_por_perfil(self, repositorio):
        curriculo = _criar_curriculo_salvo()

        repositorio.salvar(curriculo)

        assert repositorio.listar_por_perfil("matheus") == (curriculo,)

    def test_listar_por_perfil_ordena_por_data_upload_decrescente(self, repositorio):
        mais_antigo = _criar_curriculo_salvo(id="uuid-1", data_upload=datetime(2026, 1, 1, tzinfo=timezone.utc))
        mais_recente = _criar_curriculo_salvo(id="uuid-2", data_upload=datetime(2026, 6, 1, tzinfo=timezone.utc))

        repositorio.salvar(mais_antigo)
        repositorio.salvar(mais_recente)

        assert repositorio.listar_por_perfil("matheus") == (mais_recente, mais_antigo)

    def test_contar_por_perfil(self, repositorio):
        repositorio.salvar(_criar_curriculo_salvo(id="uuid-1"))
        repositorio.salvar(_criar_curriculo_salvo(id="uuid-2"))

        assert repositorio.contar_por_perfil("matheus") == 2

    def test_remover_exclui_curriculo_do_perfil(self, repositorio):
        curriculo = _criar_curriculo_salvo()
        repositorio.salvar(curriculo)

        repositorio.remover(curriculo.id, "matheus")

        assert repositorio.contar_por_perfil("matheus") == 0

    def test_isolamento_entre_perfis_diferentes(self, repositorio):
        curriculo_matheus = _criar_curriculo_salvo(id="uuid-matheus", perfil_identificador="matheus")
        curriculo_outra = _criar_curriculo_salvo(id="uuid-outra", perfil_identificador="outra-pessoa")

        repositorio.salvar(curriculo_matheus)
        repositorio.salvar(curriculo_outra)

        assert repositorio.listar_por_perfil("matheus") == (curriculo_matheus,)
        assert repositorio.listar_por_perfil("outra-pessoa") == (curriculo_outra,)

    def test_remover_nao_afeta_curriculo_de_outro_perfil(self, repositorio):
        curriculo_outra = _criar_curriculo_salvo(id="uuid-outra", perfil_identificador="outra-pessoa")
        repositorio.salvar(curriculo_outra)

        repositorio.remover(curriculo_outra.id, "matheus")

        assert repositorio.contar_por_perfil("outra-pessoa") == 1

"""Contrato de CurriculoSalvoRepository.atualizar_pdf, verificado no fake e no PostgreSQL."""
from datetime import datetime, timezone

import pytest

from jobsync.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.adapters import CurriculoSalvoRepositoryFake, CurriculoSalvoRepositoryImpl
from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl


@pytest.fixture(params=["fake", "postgres"])
def repositorio(request):
    if request.param == "fake":
        return CurriculoSalvoRepositoryFake()
    pool = request.getfixturevalue("pool_postgres")
    PerfilRepositoryImpl(pool).criar("matheus")
    PerfilRepositoryImpl(pool).criar("outra-pessoa")
    return CurriculoSalvoRepositoryImpl(pool)


def _curriculo() -> CurriculoSalvo:
    return CurriculoSalvo(
        id="salvo-1",
        perfil_identificador="matheus",
        nome_referencia="Matheus-Backend.pdf",
        pdf_bytes=b"%PDF-antigo",
        data_upload=datetime(2026, 7, 26, 10, 0, tzinfo=timezone.utc),
    )


class TestAtualizarPdf:
    def test_substitui_o_pdf_e_preserva_o_resto(self, repositorio):
        original = _curriculo()
        repositorio.salvar(original)

        atualizado = repositorio.atualizar_pdf("salvo-1", "matheus", b"%PDF-novo")

        assert atualizado is True
        (guardado,) = repositorio.listar_por_perfil("matheus")
        assert guardado.pdf_bytes == b"%PDF-novo"
        assert guardado.nome_referencia == original.nome_referencia
        assert guardado.data_upload == original.data_upload

    def test_curriculo_inexistente_devolve_false(self, repositorio):
        assert repositorio.atualizar_pdf("nao-existe", "matheus", b"%PDF-novo") is False

    def test_curriculo_de_outro_perfil_devolve_false_e_nao_altera(self, repositorio):
        repositorio.salvar(_curriculo())

        atualizado = repositorio.atualizar_pdf("salvo-1", "outra-pessoa", b"%PDF-novo")

        assert atualizado is False
        assert repositorio.listar_por_perfil("matheus")[0].pdf_bytes == b"%PDF-antigo"

"""Testes de invariantes de VagaExterna, FonteVagaExterna e VagaComScore."""

from datetime import date

import pytest

from domain.ats_score import ResultadoAtsScore
from domain.vaga_externa import FonteVagaExterna, VagaComScore, VagaExterna


def _criar_vaga_externa(**overrides) -> VagaExterna:
    dados = dict(
        titulo="Engenheiro de Software Backend",
        empresa="TechCorp",
        descricao="Vaga remota para engenheiro backend com Python.",
        url="https://exemplo.com/vaga/1",
        fonte=FonteVagaExterna.REMOTEOK,
    )
    dados.update(overrides)
    return VagaExterna(**dados)


class TestVagaExterna:
    def test_criar_vaga_externa_valida(self):
        vaga = _criar_vaga_externa()

        assert vaga.titulo == "Engenheiro de Software Backend"
        assert vaga.fonte == FonteVagaExterna.REMOTEOK
        assert vaga.descricao_incompleta is False
        assert vaga.data_publicacao is None

    def test_criar_vaga_externa_com_data_publicacao(self):
        vaga = _criar_vaga_externa(data_publicacao=date(2026, 7, 20))

        assert vaga.data_publicacao == date(2026, 7, 20)

    def test_titulo_vazio_levanta_erro(self):
        with pytest.raises(ValueError):
            _criar_vaga_externa(titulo="")

    def test_empresa_vazia_levanta_erro(self):
        with pytest.raises(ValueError):
            _criar_vaga_externa(empresa="   ")

    def test_descricao_vazia_levanta_erro(self):
        with pytest.raises(ValueError):
            _criar_vaga_externa(descricao="")

    def test_url_vazia_levanta_erro(self):
        with pytest.raises(ValueError):
            _criar_vaga_externa(url="")


class TestVagaComScore:
    def test_criar_vaga_com_score(self):
        vaga = _criar_vaga_externa()
        resultado = ResultadoAtsScore(nota=80, requisitos_faltantes=())

        vaga_com_score = VagaComScore(vaga=vaga, resultado_score=resultado)

        assert vaga_com_score.vaga == vaga
        assert vaga_com_score.resultado_score.nota == 80

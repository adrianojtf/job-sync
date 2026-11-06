import pytest

from jobsync.shared_kernel.domain import (
    ResultadoDimensaoAvaliacao,
    calcular_score_geral,
)


_LEGENDA = {
    0: "muito insuficiente",
    1: "insuficiente",
    2: "parcial",
    3: "adequado",
    4: "muito bom",
}
_PROBABILIDADES = {0: 0.1, 1: 0.2, 2: 0.4, 3: 0.2, 4: 0.1}


class TestResultadoDimensaoAvaliacao:
    def test_normaliza_os_limites_da_escala_ordinal(self):
        score_minimo = ResultadoDimensaoAvaliacao.normalizar(
            0, _PROBABILIDADES, _LEGENDA, 0.8
        )
        score_maximo = ResultadoDimensaoAvaliacao.normalizar(
            4, _PROBABILIDADES, _LEGENDA, 0.9
        )

        assert score_minimo.score == 0
        assert score_maximo.score == 100

    def test_normaliza_valor_intermediario_e_preserva_nivel_e_confianca(self):
        resultado = ResultadoDimensaoAvaliacao.normalizar(
            1.5, _PROBABILIDADES, _LEGENDA, 0.72
        )

        assert resultado.score == 38
        assert resultado.nivel == "parcial"
        assert resultado.confianca == 0.72

    def test_desempata_probabilidades_escolhendo_o_nivel_inferior(self):
        resultado = ResultadoDimensaoAvaliacao.normalizar(
            2.5,
            {0: 0.1, 1: 0.2, 2: 0.3, 3: 0.3, 4: 0.1},
            _LEGENDA,
            0.5,
        )

        assert resultado.nivel == "parcial"

    @pytest.mark.parametrize(
        ("score", "probabilidades", "legenda", "confianca"),
        [
            (4.1, _PROBABILIDADES, _LEGENDA, 0.8),
            (1, _PROBABILIDADES, _LEGENDA, 1.2),
            (1, {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1}, _LEGENDA, 0.5),
            (1, _PROBABILIDADES, {0: "baixo", 1: "medio", 2: "", 3: "alto", 4: "muito alto"}, 0.5),
            (1, _PROBABILIDADES, {0: "baixo", 1: "medio", 2: "adequado", 3: "alto", 5: "muito alto"}, 0.5),
        ],
    )
    def test_dados_ordinais_invalidos_sao_rejeitados(
        self, score, probabilidades, legenda, confianca
    ):
        with pytest.raises(ValueError):
            ResultadoDimensaoAvaliacao.normalizar(
                score, probabilidades, legenda, confianca
            )


def test_calcular_score_geral_retorna_media_aritmetica_arredondada():
    dimensoes = (
        ResultadoDimensaoAvaliacao(50, "parcial", 0.7),
        ResultadoDimensaoAvaliacao(70, "adequado", 0.8),
        ResultadoDimensaoAvaliacao(80, "bom", 0.9),
    )

    assert calcular_score_geral(dimensoes) == 67


def test_calcular_score_geral_rejeita_uma_avaliacao_sem_dimensoes():
    with pytest.raises(ValueError, match="pelo menos uma dimensão"):
        calcular_score_geral(())

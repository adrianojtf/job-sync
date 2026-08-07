"""Testes do value object ResultadoAtsScore."""

from jobsync.vaga import (
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.ats_score import ResultadoAtsScore


class TestResultadoAtsScore:
    def test_cria_resultado_com_nota_e_faltantes(self):
        requisito = RequisitoTecnico(
            nome="Docker",
            categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
            tipo=TipoRequisitoTecnico.EXPLICITO,
            origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
        )
        resultado = ResultadoAtsScore(nota=80, requisitos_faltantes=(requisito,))

        assert resultado.nota == 80
        assert resultado.requisitos_faltantes == (requisito,)

    def test_permite_lista_de_faltantes_vazia(self):
        resultado = ResultadoAtsScore(nota=100, requisitos_faltantes=())

        assert resultado.requisitos_faltantes == ()

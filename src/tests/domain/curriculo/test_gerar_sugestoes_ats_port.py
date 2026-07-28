"""Testes de porta para o gerador de sugestões de ATS."""

from domain.ats_score import ResultadoAtsScore
from domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from domain.curriculo.gerar_sugestoes_ats_port import GerarSugestoesAtsPort
from domain.vaga import AnaliseVaga


class GerarSugestoesAtsFake(GerarSugestoesAtsPort):
    def gerar(
        self, curriculo: Curriculo, analise_vaga: AnaliseVaga, resultado_ats: ResultadoAtsScore
    ) -> tuple[str, ...]:
        return (f"Sugestões para nota {resultado_ats.nota}",)


def test_gerar_sugestoes_ats_port_eh_interface_pura() -> None:
    curriculo = Curriculo(
        nome_completo="Fulano de Tal",
        email="fulano@example.com",
        linkedin="linkedin.com/in/fulano",
        secoes=(SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro backend."),),
    )
    analise = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
    resultado_ats = ResultadoAtsScore(nota=80, requisitos_faltantes=())
    fake = GerarSugestoesAtsFake()

    sugestoes = fake.gerar(curriculo, analise, resultado_ats)

    assert sugestoes == ("Sugestões para nota 80",)

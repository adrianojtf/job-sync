"""Testes de porta para o gerador de carta de apresentação."""

from domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from domain.curriculo.gerar_carta_apresentacao_port import GerarCartaApresentacaoPort
from domain.vaga import AnaliseVaga


class GerarCartaApresentacaoFake(GerarCartaApresentacaoPort):
    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, idioma_alvo: str) -> str:
        return f"Carta para {curriculo.nome_completo} em {idioma_alvo}"


def test_gerar_carta_apresentacao_port_eh_interface_pura() -> None:
    curriculo = Curriculo(
        nome_completo="Fulano de Tal",
        email="fulano@example.com",
        linkedin="linkedin.com/in/fulano",
        secoes=(SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro backend."),),
    )
    analise = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
    fake = GerarCartaApresentacaoFake()

    carta = fake.gerar(curriculo, analise, "pt")

    assert carta == "Carta para Fulano de Tal em pt"

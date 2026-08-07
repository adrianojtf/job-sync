"""Testes do caso de uso GerarCartaApresentacao."""

from jobsync.curriculo.service_layer.gerar_carta_apresentacao import GerarCartaApresentacao
from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.domain.gerar_carta_apresentacao_port import GerarCartaApresentacaoPort
from jobsync.vaga import AnaliseVaga


class GerarCartaApresentacaoFake(GerarCartaApresentacaoPort):
    def __init__(self, carta_a_retornar: str):
        self._carta = carta_a_retornar
        self.chamada: tuple[Curriculo, AnaliseVaga, str] | None = None

    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, idioma_alvo: str) -> str:
        self.chamada = (curriculo, analise_vaga, idioma_alvo)
        return self._carta


def _curriculo() -> Curriculo:
    return Curriculo(
        nome_completo="Fulano de Tal",
        email="fulano@example.com",
        linkedin="linkedin.com/in/fulano",
        secoes=(SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro backend."),),
    )


class TestGerarCartaApresentacao:
    def test_repassa_curriculo_analise_e_idioma_para_a_porta(self):
        curriculo = _curriculo()
        analise = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
        fake = GerarCartaApresentacaoFake("Carta gerada")
        use_case = GerarCartaApresentacao(gerador_carta=fake)

        resultado = use_case.executar(curriculo, analise, idioma_alvo="pt")

        assert fake.chamada == (curriculo, analise, "pt")
        assert resultado == "Carta gerada"

    def test_retorna_texto_da_porta_sem_alteracao(self):
        fake = GerarCartaApresentacaoFake("Dear hiring manager, ...")
        use_case = GerarCartaApresentacao(gerador_carta=fake)

        resultado = use_case.executar(
            _curriculo(),
            AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga"),
            idioma_alvo="en",
        )

        assert resultado == "Dear hiring manager, ..."

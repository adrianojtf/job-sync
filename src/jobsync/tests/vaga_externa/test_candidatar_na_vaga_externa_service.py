"""Testes do caso de uso CandidatarNaVagaExterna."""

import pytest

from jobsync.ats_score import CalcularAtsScore
from jobsync.curriculo import (
    AjustadorTextoPort,
    Curriculo,
    ExtratorCurriculoPort,
    GeradorPdfPort,
    GerarCartaApresentacaoPort,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.vaga import AnaliseVaga
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort
from jobsync.vaga_externa import FonteVagaExterna, VagaExterna
from jobsync.vaga_externa.service_layer.candidatar_na_vaga_externa import (
    CandidatarNaVagaExterna,
    CandidatarNaVagaExternaInputDto,
)


class ExtratorFake(ExtratorCurriculoPort):
    def __init__(self, curriculo: Curriculo):
        self._curriculo = curriculo
        self.chamado = False

    def extrair(self, conteudo_pdf: bytes) -> Curriculo:
        self.chamado = True
        return self._curriculo


class JobDescriptionAnalyzerFake(JobDescriptionAnalyzerPort):
    def __init__(self, analise: AnaliseVaga):
        self._analise = analise
        self.recebeu_descricao: str | None = None

    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        self.recebeu_descricao = descricao_vaga
        return self._analise


class AjustadorTextoFake(AjustadorTextoPort):
    def __init__(self):
        self.chamadas = 0

    def ajustar_secao(self, secao, descricao_vaga, idioma_alvo, analise_vaga):
        self.chamadas += 1
        return secao.com_novo_conteudo(f"[AJUSTADO] {secao.conteudo}")


class GeradorPdfFake(GeradorPdfPort):
    def gerar(self, curriculo: Curriculo, idioma_alvo: str) -> bytes:
        return b"%PDF-FAKE-CONTENT"


class GerarCartaApresentacaoFake(GerarCartaApresentacaoPort):
    def __init__(self, carta: str = "Carta de apresentação gerada."):
        self._carta = carta
        self.chamada: tuple[Curriculo, AnaliseVaga, str] | None = None

    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, idioma_alvo: str) -> str:
        self.chamada = (curriculo, analise_vaga, idioma_alvo)
        return self._carta


def _curriculo() -> Curriculo:
    return Curriculo(
        nome_completo="Fulano de Tal",
        email="fulano@example.com",
        linkedin="linkedin.com/in/fulano",
        secoes=(SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Python, Docker"),),
    )


def _vaga_externa() -> VagaExterna:
    return VagaExterna(
        titulo="Engenheiro de Software Backend",
        empresa="TechCorp",
        descricao="Vaga remota para engenheiro backend com Python.",
        url="https://exemplo.com/vaga/1",
        fonte=FonteVagaExterna.REMOTEOK,
    )


def _input_dto(**overrides) -> CandidatarNaVagaExternaInputDto:
    dados = dict(
        pdf_curriculo=b"conteudo-pdf",
        vaga=_vaga_externa(),
        idioma_alvo="pt",
        cargo_alvo="Engenheiro de Software",
        empresa_alvo="TechCorp",
    )
    dados.update(overrides)
    return CandidatarNaVagaExternaInputDto(**dados)


def _use_case(
    analise: AnaliseVaga | None = None,
    gerador_carta: GerarCartaApresentacaoFake | None = None,
) -> CandidatarNaVagaExterna:
    analise = analise or AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
    return CandidatarNaVagaExterna(
        extrator=ExtratorFake(_curriculo()),
        analisador_vaga=JobDescriptionAnalyzerFake(analise),
        ajustador_texto=AjustadorTextoFake(),
        gerador_pdf=GeradorPdfFake(),
        calcular_ats_score=CalcularAtsScore(),
        gerador_carta=gerador_carta or GerarCartaApresentacaoFake(),
    )


class TestCandidatarNaVagaExterna:
    def test_retorna_pdf_ats_carta_e_url_da_vaga(self):
        use_case = _use_case()

        resultado = use_case.executar(_input_dto())

        assert resultado.pdf_bytes == b"%PDF-FAKE-CONTENT"
        assert resultado.resultado_ats.nota == 100
        assert resultado.carta_apresentacao == "Carta de apresentação gerada."
        assert resultado.url_vaga == "https://exemplo.com/vaga/1"
        assert resultado.nome_arquivo.valor.startswith("FulanoDeTal-")

    def test_url_vaga_e_repassada_sem_alteracao(self):
        use_case = _use_case()
        vaga = VagaExterna(
            titulo="Outra Vaga",
            empresa="OutraEmpresa",
            descricao="descricao qualquer",
            url="https://outraempresa.com/carreiras/42",
            fonte=FonteVagaExterna.ARBEITNOW,
        )

        resultado = use_case.executar(_input_dto(vaga=vaga))

        assert resultado.url_vaga == "https://outraempresa.com/carreiras/42"

    def test_carta_e_gerada_com_curriculo_adaptado_e_analise_da_vaga(self):
        analise = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
        gerador_carta = GerarCartaApresentacaoFake()
        use_case = _use_case(analise=analise, gerador_carta=gerador_carta)

        use_case.executar(_input_dto())

        curriculo_recebido, analise_recebida, idioma_recebido = gerador_carta.chamada
        assert analise_recebida is analise
        assert idioma_recebido == "pt"
        assert curriculo_recebido.obter_secao(TipoSecao.TECNOLOGIAS).conteudo == "[AJUSTADO] Python, Docker"

    def test_pdf_vazio_gera_erro(self):
        use_case = _use_case()

        with pytest.raises(ValueError, match="PDF"):
            use_case.executar(_input_dto(pdf_curriculo=b""))

    def test_idioma_vazio_gera_erro(self):
        use_case = _use_case()

        with pytest.raises(ValueError, match="idioma"):
            use_case.executar(_input_dto(idioma_alvo="   "))

    def test_curriculo_pre_montado_pula_extracao_via_ia(self):
        curriculo = _curriculo()
        extrator = ExtratorFake(curriculo)
        use_case = CandidatarNaVagaExterna(
            extrator=extrator,
            analisador_vaga=JobDescriptionAnalyzerFake(
                AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
            ),
            ajustador_texto=AjustadorTextoFake(),
            gerador_pdf=GeradorPdfFake(),
            calcular_ats_score=CalcularAtsScore(),
            gerador_carta=GerarCartaApresentacaoFake(),
        )

        resultado = use_case.executar(_input_dto(pdf_curriculo=None, curriculo_pre_montado=curriculo))

        assert extrator.chamado is False
        assert resultado.pdf_bytes == b"%PDF-FAKE-CONTENT"

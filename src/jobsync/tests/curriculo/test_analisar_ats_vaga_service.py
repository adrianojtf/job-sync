"""Testes do caso de uso AnalisarAtsVaga."""

import pytest

from jobsync.curriculo.service_layer.analisar_ats_vaga import AnalisarAtsVaga, AnalisarAtsVagaInputDto
from jobsync.ats_score import ResultadoAtsScore
from jobsync.ats_score.domain.calcular_ats_score_service import CalcularAtsScore
from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.gerar_sugestoes_ats_port import GerarSugestoesAtsPort
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort


class ExtratorFake(ExtratorCurriculoPort):
    def __init__(self, curriculo: Curriculo):
        self._curriculo = curriculo
        self.recebeu_pdf: bytes | None = None

    def extrair(self, conteudo_pdf: bytes) -> Curriculo:
        self.recebeu_pdf = conteudo_pdf
        return self._curriculo


class JobDescriptionAnalyzerFake(JobDescriptionAnalyzerPort):
    def __init__(self, analise: AnaliseVaga):
        self._analise = analise
        self.recebeu_descricao: str | None = None

    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        self.recebeu_descricao = descricao_vaga
        return self._analise


class GerarSugestoesAtsFake(GerarSugestoesAtsPort):
    def __init__(self, sugestoes: tuple[str, ...]):
        self._sugestoes = sugestoes
        self.chamada: tuple[Curriculo, AnaliseVaga, ResultadoAtsScore] | None = None

    def gerar(
        self, curriculo: Curriculo, analise_vaga: AnaliseVaga, resultado_ats: ResultadoAtsScore
    ) -> tuple[str, ...]:
        self.chamada = (curriculo, analise_vaga, resultado_ats)
        return self._sugestoes


def _curriculo() -> Curriculo:
    return Curriculo(
        nome_completo="Fulano de Tal",
        email="fulano@example.com",
        linkedin="linkedin.com/in/fulano",
        secoes=(SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Python, Docker"),),
    )


def _analise_com_requisito_faltante() -> AnaliseVaga:
    return AnaliseVaga(
        requisitos=(
            RequisitoTecnico(
                nome="Kubernetes",
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            ),
        ),
        ambiguidade=(),
        texto_original="Vaga que exige Kubernetes",
    )


class TestAnalisarAtsVaga:
    def test_executa_pipeline_completo_sem_adaptar_secoes(self):
        curriculo = _curriculo()
        extrator = ExtratorFake(curriculo)
        analise = _analise_com_requisito_faltante()
        analisador = JobDescriptionAnalyzerFake(analise)
        gerador_sugestoes = GerarSugestoesAtsFake(("Adicione Kubernetes na seção de Tecnologias.",))
        use_case = AnalisarAtsVaga(
            extrator=extrator,
            analisador_vaga=analisador,
            calcular_ats_score=CalcularAtsScore(),
            gerador_sugestoes=gerador_sugestoes,
        )

        resultado = use_case.executar(
            AnalisarAtsVagaInputDto(pdf_curriculo=b"conteudo-pdf", descricao_vaga="Vaga que exige Kubernetes")
        )

        assert extrator.recebeu_pdf == b"conteudo-pdf"
        assert analisador.recebeu_descricao == "Vaga que exige Kubernetes"
        assert resultado.curriculo == curriculo
        assert resultado.analise_vaga == analise
        assert resultado.resultado_ats.nota == 0
        assert [r.nome for r in resultado.resultado_ats.requisitos_faltantes] == ["Kubernetes"]
        assert resultado.sugestoes == ("Adicione Kubernetes na seção de Tecnologias.",)
        assert gerador_sugestoes.chamada == (curriculo, analise, resultado.resultado_ats)

    def test_descricao_vaga_vazia_gera_erro(self):
        use_case = AnalisarAtsVaga(
            extrator=ExtratorFake(_curriculo()),
            analisador_vaga=JobDescriptionAnalyzerFake(_analise_com_requisito_faltante()),
            calcular_ats_score=CalcularAtsScore(),
            gerador_sugestoes=GerarSugestoesAtsFake(("sugestoes",)),
        )

        with pytest.raises(ValueError, match="descrição da vaga"):
            use_case.executar(AnalisarAtsVagaInputDto(pdf_curriculo=b"pdf", descricao_vaga="   "))

    def test_pdf_vazio_gera_erro(self):
        use_case = AnalisarAtsVaga(
            extrator=ExtratorFake(_curriculo()),
            analisador_vaga=JobDescriptionAnalyzerFake(_analise_com_requisito_faltante()),
            calcular_ats_score=CalcularAtsScore(),
            gerador_sugestoes=GerarSugestoesAtsFake(("sugestoes",)),
        )

        with pytest.raises(ValueError, match="PDF"):
            use_case.executar(AnalisarAtsVagaInputDto(pdf_curriculo=b"", descricao_vaga="vaga"))

    def test_curriculo_pre_montado_pula_extracao_via_ia(self):
        curriculo = _curriculo()
        extrator = ExtratorFake(curriculo)
        use_case = AnalisarAtsVaga(
            extrator=extrator,
            analisador_vaga=JobDescriptionAnalyzerFake(_analise_com_requisito_faltante()),
            calcular_ats_score=CalcularAtsScore(),
            gerador_sugestoes=GerarSugestoesAtsFake(("sugestoes",)),
        )

        resultado = use_case.executar(
            AnalisarAtsVagaInputDto(curriculo_pre_montado=curriculo, descricao_vaga="Vaga que exige Kubernetes")
        )

        assert extrator.recebeu_pdf is None
        assert resultado.curriculo == curriculo

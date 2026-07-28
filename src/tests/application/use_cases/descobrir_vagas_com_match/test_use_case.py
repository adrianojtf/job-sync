"""Testes do caso de uso DescobrirVagasComMatch."""

from datetime import date, timedelta

import pytest

from application.use_cases.descobrir_vagas_com_match import (
    LIMITE_VAGAS_ANALISADAS,
    DescobrirVagasComMatch,
)
from domain.ats_score.calcular_ats_score_service import CalcularAtsScore
from domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from domain.curriculo.extrator_curriculo_port import ExtratorCurriculoPort
from domain.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from domain.vaga.job_description_analyzer_port import JobDescriptionAnalyzerPort
from domain.vaga_externa import FonteVagaExterna, VagaExterna
from domain.vaga_externa.buscador_vagas_externo_port import BuscadorVagasExternoPort


class BuscadorFake(BuscadorVagasExternoPort):
    def __init__(self, vagas: tuple[VagaExterna, ...] = (), erro: Exception | None = None):
        self._vagas = vagas
        self._erro = erro

    def buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]:
        if self._erro is not None:
            raise self._erro
        return self._vagas


class ExtratorFake(ExtratorCurriculoPort):
    def __init__(self, curriculo: Curriculo):
        self._curriculo = curriculo

    def extrair(self, conteudo_pdf: bytes) -> Curriculo:
        return self._curriculo


class JobDescriptionAnalyzerFake(JobDescriptionAnalyzerPort):
    def __init__(self, analises_por_descricao: dict[str, AnaliseVaga]):
        self._analises_por_descricao = analises_por_descricao

    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        return self._analises_por_descricao[descricao_vaga]


def _curriculo() -> Curriculo:
    return Curriculo(
        nome_completo="Fulano de Tal",
        email="fulano@example.com",
        linkedin="linkedin.com/in/fulano",
        secoes=(SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Python, Docker"),),
    )


def _analise_sem_requisitos_faltantes() -> AnaliseVaga:
    return AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga sem requisitos explícitos")


def _analise_com_requisito_faltante(nome_requisito: str, texto_original: str) -> AnaliseVaga:
    return AnaliseVaga(
        requisitos=(
            RequisitoTecnico(
                nome=nome_requisito,
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            ),
        ),
        ambiguidade=(),
        texto_original=texto_original,
    )


def _vaga_externa(**overrides) -> VagaExterna:
    dados = dict(
        titulo="Engenheiro de Software Backend",
        empresa="TechCorp",
        descricao="vaga sem requisitos explícitos",
        url="https://exemplo.com/vaga/1",
        fonte=FonteVagaExterna.REMOTEOK,
    )
    dados.update(overrides)
    return VagaExterna(**dados)


class TestDescobrirVagasComMatch:
    def test_deduplica_vagas_com_mesmo_titulo_e_empresa(self):
        vaga = _vaga_externa()
        vaga_duplicada = _vaga_externa(fonte=FonteVagaExterna.ARBEITNOW)
        use_case = DescobrirVagasComMatch(
            buscadores=(BuscadorFake((vaga,)), BuscadorFake((vaga_duplicada,))),
            analisador_vaga=JobDescriptionAnalyzerFake(
                {"vaga sem requisitos explícitos": _analise_sem_requisitos_faltantes()}
            ),
            extrator_curriculo=ExtratorFake(_curriculo()),
            calcular_score=CalcularAtsScore(),
        )

        resultado = use_case.executar("backend", b"conteudo-pdf")

        assert len(resultado) == 1

    def test_ordena_por_score_decrescente(self):
        vaga_score_alto = _vaga_externa(titulo="Vaga A", descricao="descricao sem requisito")
        vaga_score_baixo = _vaga_externa(
            titulo="Vaga B", empresa="OutraEmpresa", descricao="descricao com kubernetes"
        )
        use_case = DescobrirVagasComMatch(
            buscadores=(BuscadorFake((vaga_score_alto, vaga_score_baixo)),),
            analisador_vaga=JobDescriptionAnalyzerFake(
                {
                    "descricao sem requisito": _analise_sem_requisitos_faltantes(),
                    "descricao com kubernetes": _analise_com_requisito_faltante(
                        "Kubernetes", "descricao com kubernetes"
                    ),
                }
            ),
            extrator_curriculo=ExtratorFake(_curriculo()),
            calcular_score=CalcularAtsScore(),
        )

        resultado = use_case.executar("engenheiro", b"conteudo-pdf")

        assert len(resultado) == 2
        assert resultado[0].vaga.titulo == "Vaga A"
        assert resultado[0].resultado_score.nota == 100
        assert resultado[1].vaga.titulo == "Vaga B"
        assert resultado[1].resultado_score.nota == 0

    def test_falha_de_uma_fonte_nao_impede_demais(self):
        vaga_ok = _vaga_externa()
        use_case = DescobrirVagasComMatch(
            buscadores=(BuscadorFake((vaga_ok,)), BuscadorFake(erro=TimeoutError("fonte indisponível"))),
            analisador_vaga=JobDescriptionAnalyzerFake(
                {"vaga sem requisitos explícitos": _analise_sem_requisitos_faltantes()}
            ),
            extrator_curriculo=ExtratorFake(_curriculo()),
            calcular_score=CalcularAtsScore(),
        )

        resultado = use_case.executar("backend", b"conteudo-pdf")

        assert len(resultado) == 1
        assert resultado[0].vaga == vaga_ok

    def test_limita_quantidade_de_vagas_analisadas_por_ia(self):
        vagas = tuple(
            _vaga_externa(titulo=f"Vaga {i}", empresa=f"Empresa {i}") for i in range(LIMITE_VAGAS_ANALISADAS + 10)
        )
        use_case = DescobrirVagasComMatch(
            buscadores=(BuscadorFake(vagas),),
            analisador_vaga=JobDescriptionAnalyzerFake(
                {"vaga sem requisitos explícitos": _analise_sem_requisitos_faltantes()}
            ),
            extrator_curriculo=ExtratorFake(_curriculo()),
            calcular_score=CalcularAtsScore(),
        )

        resultado = use_case.executar("backend", b"conteudo-pdf")

        assert len(resultado) == LIMITE_VAGAS_ANALISADAS

    def test_filtro_de_periodo_remove_vaga_fora_da_janela(self):
        hoje = date.today()
        vaga_recente = _vaga_externa(
            titulo="Vaga Recente", data_publicacao=hoje - timedelta(days=3)
        )
        vaga_antiga = _vaga_externa(
            titulo="Vaga Antiga", empresa="OutraEmpresa", data_publicacao=hoje - timedelta(days=40)
        )
        use_case = DescobrirVagasComMatch(
            buscadores=(BuscadorFake((vaga_recente, vaga_antiga)),),
            analisador_vaga=JobDescriptionAnalyzerFake(
                {"vaga sem requisitos explícitos": _analise_sem_requisitos_faltantes()}
            ),
            extrator_curriculo=ExtratorFake(_curriculo()),
            calcular_score=CalcularAtsScore(),
        )

        resultado = use_case.executar("backend", b"conteudo-pdf", dias_maximo=7)

        assert len(resultado) == 1
        assert resultado[0].vaga.titulo == "Vaga Recente"

    def test_filtro_de_periodo_mantem_vaga_com_data_desconhecida(self):
        vaga_sem_data = _vaga_externa(titulo="Vaga Sem Data", data_publicacao=None)
        use_case = DescobrirVagasComMatch(
            buscadores=(BuscadorFake((vaga_sem_data,)),),
            analisador_vaga=JobDescriptionAnalyzerFake(
                {"vaga sem requisitos explícitos": _analise_sem_requisitos_faltantes()}
            ),
            extrator_curriculo=ExtratorFake(_curriculo()),
            calcular_score=CalcularAtsScore(),
        )

        resultado = use_case.executar("backend", b"conteudo-pdf", dias_maximo=7)

        assert len(resultado) == 1
        assert resultado[0].vaga.titulo == "Vaga Sem Data"

    def test_sem_dias_maximo_nenhuma_vaga_e_removida_por_data(self):
        hoje = date.today()
        vaga_antiga = _vaga_externa(titulo="Vaga Antiga", data_publicacao=hoje - timedelta(days=400))
        use_case = DescobrirVagasComMatch(
            buscadores=(BuscadorFake((vaga_antiga,)),),
            analisador_vaga=JobDescriptionAnalyzerFake(
                {"vaga sem requisitos explícitos": _analise_sem_requisitos_faltantes()}
            ),
            extrator_curriculo=ExtratorFake(_curriculo()),
            calcular_score=CalcularAtsScore(),
        )

        resultado = use_case.executar("backend", b"conteudo-pdf")

        assert len(resultado) == 1

    def test_termo_vazio_gera_erro(self):
        use_case = DescobrirVagasComMatch(
            buscadores=(),
            analisador_vaga=JobDescriptionAnalyzerFake({}),
            extrator_curriculo=ExtratorFake(_curriculo()),
            calcular_score=CalcularAtsScore(),
        )

        with pytest.raises(ValueError, match="termo"):
            use_case.executar("   ", b"conteudo-pdf")

    def test_pdf_vazio_gera_erro(self):
        use_case = DescobrirVagasComMatch(
            buscadores=(),
            analisador_vaga=JobDescriptionAnalyzerFake({}),
            extrator_curriculo=ExtratorFake(_curriculo()),
            calcular_score=CalcularAtsScore(),
        )

        with pytest.raises(ValueError, match="PDF"):
            use_case.executar("backend", b"")

"""API real para os testes E2E da UI, com dublês apenas nas portas de IA e de busca externa.

Repositórios (SQLite), casos de uso, gerador de PDF e cálculo de ATS são os de produção.
Os dublês devolvem respostas determinísticas, sem rede e sem chaves de API.

Uso: PYTHONPATH=src DATABASE_PATH=<arquivo.db> uvicorn jobsync.tests.e2e.app_e2e:app --port 8010
"""
from __future__ import annotations

import os
from pathlib import Path

from jobsync.ats_score import CalcularAtsScore, ResultadoAtsScore
from jobsync.curriculo import AvaliacaoExperiencia, Curriculo, ExperienciaParaAvaliacao, SecaoCurriculo, TipoSecao
from jobsync.curriculo.adapters.gerador_pdf_client import GeradorPdfClient
from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.avaliador_experiencia_port import AvaliadorExperienciaPort
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.gerar_carta_apresentacao_port import GerarCartaApresentacaoPort
from jobsync.curriculo.domain.gerar_sugestoes_ats_port import GerarSugestoesAtsPort
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import AdaptarCurriculoParaVaga
from jobsync.curriculo.service_layer.analisar_ats_vaga import AnalisarAtsVaga
from jobsync.curriculo.service_layer.avaliar_experiencia import AvaliarExperiencia
from jobsync.curriculo.service_layer.gerar_carta_apresentacao.service import GerarCartaApresentacao
from jobsync.entrypoints.api import dependencies
from jobsync.entrypoints.api.main import app
from jobsync.shared_kernel.domain.score_avaliacao import ResultadoDimensaoAvaliacao
from jobsync.vaga import (
    AnaliseVaga,
    AvaliacaoDescricaoVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.vaga.domain.avaliador_descricao_vaga_port import AvaliadorDescricaoVagaPort
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort
from jobsync.vaga.service_layer.avaliar_descricao_vaga import AvaliarDescricaoVaga
from jobsync.vaga_externa import FonteVagaExterna, VagaExterna
from jobsync.vaga_externa.domain.buscador_vagas_externo_port import BuscadorVagasExternoPort
from jobsync.vaga_externa.service_layer.candidatar_na_vaga_externa import CandidatarNaVagaExterna
from jobsync.vaga_externa.service_layer.descobrir_vagas_com_match import DescobrirVagasComMatch

TECNOLOGIAS_CONHECIDAS = ("Python", "FastAPI", "Java", "Kafka", "AWS", "Docker")


def _dimensao(score: int, nivel: str) -> ResultadoDimensaoAvaliacao:
    return ResultadoDimensaoAvaliacao(score, nivel, 0.9)


class AnalisadorVagaE2E(JobDescriptionAnalyzerPort):
    """Considera requisito explícito cada tecnologia conhecida citada na descrição."""

    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        requisitos = tuple(
            RequisitoTecnico(
                nome=nome,
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            )
            for nome in TECNOLOGIAS_CONHECIDAS
            if nome.lower() in descricao_vaga.lower()
        )
        return AnaliseVaga(requisitos=requisitos, ambiguidade=(), texto_original=descricao_vaga)


class AjustadorTextoE2E(AjustadorTextoPort):
    def ajustar_secao(self, secao: SecaoCurriculo, descricao_vaga: str, idioma_alvo: str, analise_vaga: AnaliseVaga) -> SecaoCurriculo:
        return secao


class AjustadorExperienciaE2E(AjustadorExperienciaPort):
    def ajustar(
        self, experiencia: ExperienciaParaAvaliacao, descricao_vaga: str, idioma_alvo: str, analise_vaga: AnaliseVaga
    ) -> ExperienciaParaAvaliacao:
        return experiencia


class AvaliadorDescricaoVagaE2E(AvaliadorDescricaoVagaPort):
    def avaliar(self, descricao_vaga: str) -> AvaliacaoDescricaoVaga:
        return AvaliacaoDescricaoVaga(
            completude=_dimensao(75, "adequada"),
            clareza=_dimensao(80, "clara"),
            relevancia=_dimensao(85, "relevante"),
            inclusao=_dimensao(70, "inclusiva"),
        )


class AvaliadorExperienciaE2E(AvaliadorExperienciaPort):
    def avaliar(self, experiencia: ExperienciaParaAvaliacao, descricao_vaga: str) -> AvaliacaoExperiencia:
        return AvaliacaoExperiencia(
            clareza_escrita=_dimensao(80, "clara"),
            qualidade_detalhe=_dimensao(65, "parcial"),
            aderencia_vaga=_dimensao(88, "alta"),
            consistencia_textual=_dimensao(77, "consistente"),
        )


class ExtratorCurriculoE2E(ExtratorCurriculoPort):
    """Devolve um currículo fixo para fluxos que partem de um PDF da biblioteca."""

    def extrair(self, conteudo_pdf: bytes) -> Curriculo:
        return Curriculo(
            nome_completo="Pessoa E2E",
            email="e2e@jobsync.test",
            linkedin="",
            secoes=(SecaoCurriculo(tipo=TipoSecao.TECNOLOGIAS, titulo="Tecnologias", conteudo="Python, FastAPI"),),
        )


class GeradorSugestoesE2E(GerarSugestoesAtsPort):
    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, resultado_ats: ResultadoAtsScore) -> tuple[str, ...]:
        return tuple(f"Cite {requisito.nome} nas experiências em que foi usado." for requisito in resultado_ats.requisitos_faltantes)


class GeradorCartaE2E(GerarCartaApresentacaoPort):
    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, idioma_alvo: str) -> str:
        return f"Prezados recrutadores,\n\nSou {curriculo.nome_completo} e tenho interesse na vaga."


class BuscadorVagasE2E(BuscadorVagasExternoPort):
    def buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]:
        return (
            VagaExterna(
                titulo=f"Backend Engineer ({termo})",
                empresa="Globex",
                descricao="Python, FastAPI e Kafka. Remoto.",
                url="https://example.com/vagas/globex",
                fonte=FonteVagaExterna.REMOTEOK,
            ),
        )


def _adaptar() -> AdaptarCurriculoParaVaga:
    return AdaptarCurriculoParaVaga(
        extrator=ExtratorCurriculoE2E(),
        analisador_vaga=AnalisadorVagaE2E(),
        ajustador_texto=AjustadorTextoE2E(),
        avaliador_descricao_vaga=AvaliadorDescricaoVagaE2E(),
        ajustador_experiencia=AjustadorExperienciaE2E(),
        avaliador_experiencia=AvaliadorExperienciaE2E(),
    )


app.dependency_overrides.update(
    {
        dependencies.obter_service_avaliar_descricao_vaga: lambda: AvaliarDescricaoVaga(avaliador=AvaliadorDescricaoVagaE2E()),
        dependencies.obter_service_avaliar_experiencia: lambda: AvaliarExperiencia(avaliador=AvaliadorExperienciaE2E()),
        dependencies.obter_service_adaptar_curriculo: _adaptar,
        dependencies.obter_service_analisar_ats_vaga: lambda: AnalisarAtsVaga(
            extrator=ExtratorCurriculoE2E(),
            analisador_vaga=AnalisadorVagaE2E(),
            calcular_ats_score=CalcularAtsScore(),
            gerador_sugestoes=GeradorSugestoesE2E(),
        ),
        dependencies.obter_service_gerar_carta_apresentacao: lambda: GerarCartaApresentacao(gerador_carta=GeradorCartaE2E()),
        dependencies.obter_service_descobrir_vagas_com_match: lambda: DescobrirVagasComMatch(
            buscadores=(BuscadorVagasE2E(),),
            analisador_vaga=AnalisadorVagaE2E(),
            extrator_curriculo=ExtratorCurriculoE2E(),
            calcular_score=CalcularAtsScore(),
        ),
        dependencies.obter_service_candidatar_na_vaga_externa: lambda: CandidatarNaVagaExterna(
            extrator=ExtratorCurriculoE2E(),
            analisador_vaga=AnalisadorVagaE2E(),
            ajustador_texto=AjustadorTextoE2E(),
            gerador_pdf=GeradorPdfClient(),
            calcular_ats_score=CalcularAtsScore(),
            gerador_carta=GeradorCartaE2E(),
        ),
    }
)

_banco = os.getenv("DATABASE_PATH")
if _banco:
    Path(_banco).parent.mkdir(parents=True, exist_ok=True)

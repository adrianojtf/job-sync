"""Camada de domínio do Currículo."""

from jobsync.curriculo.domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.domain.avaliacao_experiencia import (
    AvaliacaoExperiencia,
    ExperienciaParaAvaliacao,
)
from jobsync.curriculo.domain.avaliador_experiencia_port import (
    AvaliadorExperienciaPort,
)
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.gerador_pdf_port import GeradorPdfPort
from jobsync.curriculo.domain.gerar_carta_apresentacao_port import GerarCartaApresentacaoPort
from jobsync.curriculo.domain.gerar_sugestoes_ats_port import GerarSugestoesAtsPort
from jobsync.curriculo.domain.rascunho_curriculo_adaptado import RascunhoCurriculoAdaptado

__all__ = [
    "Curriculo",
    "SecaoCurriculo",
    "TipoSecao",
    "AvaliacaoExperiencia",
    "ExperienciaParaAvaliacao",
    "AvaliadorExperienciaPort",
    "AjustadorTextoPort",
    "AjustadorExperienciaPort",
    "ExtratorCurriculoPort",
    "GeradorPdfPort",
    "GerarCartaApresentacaoPort",
    "GerarSugestoesAtsPort",
    "RascunhoCurriculoAdaptado",
]

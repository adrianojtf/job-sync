"""Camada de domínio do Currículo."""

from jobsync.curriculo.domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.gerador_pdf_port import GeradorPdfPort
from jobsync.curriculo.domain.gerar_carta_apresentacao_port import GerarCartaApresentacaoPort
from jobsync.curriculo.domain.gerar_sugestoes_ats_port import GerarSugestoesAtsPort

__all__ = [
    "Curriculo",
    "SecaoCurriculo",
    "TipoSecao",
    "AjustadorTextoPort",
    "ExtratorCurriculoPort",
    "GeradorPdfPort",
    "GerarCartaApresentacaoPort",
    "GerarSugestoesAtsPort",
]

"""Domínio Currículo: entidades, ports e casos de uso."""

from jobsync.curriculo.domain import (
    AjustadorTextoPort,
    Curriculo,
    ExtratorCurriculoPort,
    GeradorPdfPort,
    GerarCartaApresentacaoPort,
    GerarSugestoesAtsPort,
    SecaoCurriculo,
    TipoSecao,
)

__all__ = [
    "AjustadorTextoPort",
    "Curriculo",
    "ExtratorCurriculoPort",
    "GeradorPdfPort",
    "GerarCartaApresentacaoPort",
    "GerarSugestoesAtsPort",
    "SecaoCurriculo",
    "TipoSecao",
]

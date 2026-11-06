"""Domínio Currículo: entidades, ports e casos de uso."""

from jobsync.curriculo.domain import (
    AjustadorTextoPort,
    AjustadorExperienciaPort,
    AvaliacaoExperiencia,
    AvaliadorExperienciaPort,
    Curriculo,
    ExtratorCurriculoPort,
    ExperienciaParaAvaliacao,
    GeradorPdfPort,
    GerarCartaApresentacaoPort,
    GerarSugestoesAtsPort,
    SecaoCurriculo,
    TipoSecao,
)

__all__ = [
    "AjustadorTextoPort",
    "AjustadorExperienciaPort",
    "AvaliacaoExperiencia",
    "AvaliadorExperienciaPort",
    "Curriculo",
    "ExtratorCurriculoPort",
    "ExperienciaParaAvaliacao",
    "GeradorPdfPort",
    "GerarCartaApresentacaoPort",
    "GerarSugestoesAtsPort",
    "SecaoCurriculo",
    "TipoSecao",
]

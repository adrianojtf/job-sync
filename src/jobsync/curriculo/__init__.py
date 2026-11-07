"""Domínio Currículo: entidades, ports e casos de uso."""

from jobsync.curriculo.domain import (
    AjustadorTextoPort,
    AjustadorExperienciaPort,
    AvaliacaoExperiencia,
    AvaliadorExperienciaPort,
    ContextoVaga,
    Curriculo,
    ExperienciaAdaptada,
    ExtratorCurriculoPort,
    ExperienciaParaAvaliacao,
    GeradorPdfPort,
    GerarCartaApresentacaoPort,
    GerarSugestoesAtsPort,
    MelhoradorTextoCurriculoPort,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)

__all__ = [
    "AjustadorTextoPort",
    "AjustadorExperienciaPort",
    "AvaliacaoExperiencia",
    "AvaliadorExperienciaPort",
    "ContextoVaga",
    "Curriculo",
    "ExperienciaAdaptada",
    "ExtratorCurriculoPort",
    "ExperienciaParaAvaliacao",
    "GeradorPdfPort",
    "GerarCartaApresentacaoPort",
    "GerarSugestoesAtsPort",
    "MelhoradorTextoCurriculoPort",
    "RascunhoCurriculoAdaptado",
    "SecaoCurriculo",
    "TipoSecao",
]

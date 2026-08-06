"""Domínio ATS Score: cálculo de aderência de currículo a uma vaga."""

from jobsync.ats_score.domain.calcular_ats_score_service import CalcularAtsScore
from jobsync.ats_score.domain.resultado_ats_score import ResultadoAtsScore

__all__ = ["CalcularAtsScore", "ResultadoAtsScore"]

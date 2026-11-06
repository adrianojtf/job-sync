"""DTOs para o caso de uso AvaliarExperiencia."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao


@dataclass(frozen=True)
class AvaliarExperienciaInputDto:
    experiencia: ExperienciaParaAvaliacao
    descricao_vaga: str

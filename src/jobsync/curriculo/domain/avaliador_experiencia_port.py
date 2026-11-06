"""Porta para avaliar uma experiência profissional em relação a uma vaga."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.curriculo.domain.avaliacao_experiencia import (
    AvaliacaoExperiencia,
    ExperienciaParaAvaliacao,
)


class AvaliadorExperienciaPort(ABC):
    """Contrato de avaliação estruturada de uma experiência profissional."""

    @abstractmethod
    def avaliar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        descricao_vaga: str,
    ) -> AvaliacaoExperiencia:
        raise NotImplementedError

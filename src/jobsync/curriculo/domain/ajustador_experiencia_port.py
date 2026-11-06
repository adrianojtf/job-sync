"""Porta para adaptar individualmente o texto de uma experiência profissional."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.vaga.domain.analise_vaga import AnaliseVaga


class AjustadorExperienciaPort(ABC):
    """Contrato para reescrever uma experiência preservando seus metadados."""

    @abstractmethod
    def ajustar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> ExperienciaParaAvaliacao:
        raise NotImplementedError

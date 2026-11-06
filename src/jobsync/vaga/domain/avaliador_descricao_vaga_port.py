"""Porta para avaliar a qualidade de uma descrição de vaga."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.vaga.domain.avaliacao_descricao_vaga import AvaliacaoDescricaoVaga


class AvaliadorDescricaoVagaPort(ABC):
    """Contrato de avaliação estruturada de descrições de vagas."""

    @abstractmethod
    def avaliar(self, descricao_vaga: str) -> AvaliacaoDescricaoVaga:
        raise NotImplementedError

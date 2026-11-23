"""DTO de input para o caso de uso AdicionarConquistaAExperiencia."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdicionarConquistaAExperienciaInputDto:
    """A conquista aprovada pelo candidato e a experiência do perfil que a recebe."""

    perfil_identificador: str
    experiencia_indice: int
    texto: str

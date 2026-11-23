"""DTO de input para o caso de uso VerificarConquistasParecidas."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VerificarConquistasParecidasInputDto:
    """Texto da conquista nova e as conquistas que a tela já tem na experiência."""

    texto: str
    conquistas: tuple[str, ...]

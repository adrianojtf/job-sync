"""DTO de input para o caso de uso CriarCandidatura."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CriarCandidaturaInputDto:
    """Dados de entrada do caso de uso, vindos da interface (Streamlit)."""

    perfil_identificador: str
    vaga_id: str
    curriculo_salvo_id: str
    empresa: str
    cargo: str

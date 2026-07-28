"""DTO de input para o caso de uso ImportarPerfilDePdf."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImportarPerfilDePdfInputDto:
    """Dados de entrada do caso de uso, vindos da interface (Streamlit)."""

    pdf_curriculo: bytes

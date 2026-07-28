"""DTO de input para o caso de uso SalvarCurriculo."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SalvarCurriculoInputDto:
    """Dados de entrada do caso de uso, vindos da interface (Streamlit)."""

    perfil_identificador: str
    nome_referencia: str
    pdf_bytes: bytes

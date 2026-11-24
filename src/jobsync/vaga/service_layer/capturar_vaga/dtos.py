"""DTO de input para o caso de uso CapturarVaga."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CapturarVagaInputDto:
    """Dados de entrada do caso de uso, vindos da extensão de navegador ou da UI."""

    perfil_identificador: str
    texto_descricao: str
    url_origem: Optional[str] = None
    cargo: Optional[str] = None
    empresa: Optional[str] = None
    local: Optional[str] = None

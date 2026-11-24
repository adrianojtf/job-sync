"""DTO de input para o caso de uso ExtrairDadosVaga."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ExtrairDadosVagaInputDto:
    """Dados de entrada: o link da vaga e/ou o texto da vaga, com a pessoa que fez o pedido."""

    usuario_id: str
    url: Optional[str] = None
    texto: Optional[str] = None

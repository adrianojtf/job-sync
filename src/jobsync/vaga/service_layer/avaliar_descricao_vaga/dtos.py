"""DTOs para o caso de uso AvaliarDescricaoVaga."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AvaliarDescricaoVagaInputDto:
    descricao_vaga: str

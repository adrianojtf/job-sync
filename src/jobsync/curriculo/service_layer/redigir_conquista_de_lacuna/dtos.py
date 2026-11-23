"""DTO de input para o caso de uso RedigirConquistaDeLacuna."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.curriculo.domain.lacuna_da_vaga import LacunaDaVaga


@dataclass(frozen=True)
class RedigirConquistaDeLacunaInputDto:
    """A lacuna respondida, o caso do candidato, o cargo da experiência escolhida e o idioma."""

    lacuna: LacunaDaVaga
    caso: str
    cargo: str
    idioma_alvo: str

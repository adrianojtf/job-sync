"""Value object para o resultado do cálculo de ATS Score."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.vaga import RequisitoTecnico


@dataclass(frozen=True)
class ResultadoAtsScore:
    """Nota de aderência (0-100) e requisitos técnicos explícitos não cobertos."""

    nota: int
    requisitos_faltantes: tuple[RequisitoTecnico, ...]

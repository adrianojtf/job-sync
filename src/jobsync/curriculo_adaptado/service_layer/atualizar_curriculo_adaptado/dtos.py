"""DTO de input do caso de uso AtualizarCurriculoAdaptado."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from jobsync.curriculo import RascunhoCurriculoAdaptado


@dataclass(frozen=True)
class AtualizarCurriculoAdaptadoInputDto:
    curriculo_id: str
    perfil_identificador: str
    rascunho: RascunhoCurriculoAdaptado
    data_referencia: date | None = None

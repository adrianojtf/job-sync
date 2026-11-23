"""DTO de input do caso de uso SalvarCurriculoAdaptado."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from jobsync.curriculo import RascunhoCurriculoAdaptado
from jobsync.vaga import AnaliseVaga


@dataclass(frozen=True)
class SalvarCurriculoAdaptadoInputDto:
    """Rascunho confirmado pelo usuário e a vaga usada na adaptação."""

    perfil_identificador: str
    rascunho: RascunhoCurriculoAdaptado
    idioma_alvo: str
    cargo_alvo: str
    empresa_alvo: str
    descricao_vaga: str
    analise_vaga: AnaliseVaga
    data_referencia: date | None = None

"""Entidades de domínio para candidaturas registradas no Kanban.

`historico_status` contém, nesta fase, apenas a mudança de status mais
recente (não um histórico de auditoria completo) — o schema de persistência
não inclui uma tabela dedicada de histórico.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


class StatusCandidatura(Enum):
    """Estágios do funil de candidatura, correspondendo às colunas do Kanban."""

    APLICADO = auto()
    ENTREVISTA = auto()
    OFERTA = auto()
    REJEITADO = auto()


@dataclass(frozen=True)
class MudancaStatus:
    """Registro de uma mudança de status (nesta fase, apenas a mais recente)."""

    status: StatusCandidatura
    data: datetime


@dataclass(frozen=True)
class Candidatura:
    """Candidatura de um perfil a uma vaga, usando um currículo salvo específico."""

    id: str
    perfil_identificador: str
    vaga_id: str
    curriculo_salvo_id: str
    empresa: str
    cargo: str
    status: StatusCandidatura
    data_aplicacao: datetime
    historico_status: tuple[MudancaStatus, ...]

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("O id da candidatura não pode ser vazio.")
        if not self.perfil_identificador or not self.perfil_identificador.strip():
            raise ValueError("O identificador do perfil não pode ser vazio.")
        if not self.empresa or not self.empresa.strip():
            raise ValueError("A empresa da candidatura não pode ser vazia.")
        if not self.cargo or not self.cargo.strip():
            raise ValueError("O cargo da candidatura não pode ser vazio.")

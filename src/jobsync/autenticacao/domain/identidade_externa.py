"""Entidade IdentidadeExterna: vínculo entre um usuário e uma conta em um provedor."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class IdentidadeExterna:
    """Identificada por (provedor, subject); o e-mail nunca é a chave."""

    provedor: str
    subject: str
    usuario_id: UUID

    def __post_init__(self) -> None:
        if not self.provedor or not self.provedor.strip():
            raise ValueError("O provedor não pode ser vazio.")
        if not self.subject or not self.subject.strip():
            raise ValueError("O subject não pode ser vazio.")

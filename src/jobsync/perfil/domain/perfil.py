"""Entidade de domínio para o perfil do usuário (login simples, sem senha)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Perfil:
    """Representa um usuário identificado apenas por um identificador único."""

    identificador: str

    def __post_init__(self) -> None:
        if not self.identificador or not self.identificador.strip():
            raise ValueError("O identificador do perfil não pode ser vazio.")

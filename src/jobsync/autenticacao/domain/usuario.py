"""Entidade Usuario: a pessoa autenticada, dona de exatamente um perfil."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from jobsync.autenticacao.domain.email import Email


def novo_identificador_de_perfil() -> str:
    """Identificador opaco do perfil, sem dado pessoal em URLs ou logs."""
    return f"u-{uuid4().hex[:12]}"


@dataclass(frozen=True)
class Usuario:
    """Referencia o perfil apenas por identificador, conforme a regra entre domínios."""

    id: UUID
    email: Email
    perfil_identificador: str
    criado_em: datetime
    email_verificado: bool = False
    nome: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.perfil_identificador or not self.perfil_identificador.strip():
            raise ValueError("O identificador do perfil não pode ser vazio.")
        if self.criado_em.tzinfo is None:
            raise ValueError("O instante de criação deve ter fuso horário.")

    @classmethod
    def novo(
        cls,
        email: Email,
        perfil_identificador: str,
        agora: datetime,
        nome: Optional[str] = None,
    ) -> "Usuario":
        return cls(
            id=uuid4(),
            email=email,
            perfil_identificador=perfil_identificador,
            criado_em=agora,
            nome=nome,
        )

    def verificar_email(self) -> "Usuario":
        return replace(self, email_verificado=True)

"""Entidade TokenUsoUnico: link de confirmação de e-mail ou de redefinição de senha."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

from jobsync.autenticacao.domain._instantes import exigir_fuso


class Finalidade(str, Enum):
    CONFIRMACAO_EMAIL = "confirmacao_email"
    REDEFINICAO_SENHA = "redefinicao_senha"


@dataclass(frozen=True)
class TokenUsoUnico:
    """Só pode ser usado uma vez e dentro da validade; guarda apenas o hash do token."""

    token_hash: bytes
    usuario_id: UUID
    finalidade: Finalidade
    expira_em: datetime
    usado_em: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not self.token_hash:
            raise ValueError("O hash do token não pode ser vazio.")
        exigir_fuso(self.expira_em)

    @classmethod
    def emitir(
        cls,
        token_hash: bytes,
        usuario_id: UUID,
        finalidade: Finalidade,
        agora: datetime,
        validade: timedelta,
    ) -> "TokenUsoUnico":
        exigir_fuso(agora)
        if validade <= timedelta(0):
            raise ValueError("A validade do token deve ser positiva.")
        return cls(token_hash, usuario_id, finalidade, agora + validade)

    def utilizavel(self, agora: datetime) -> bool:
        return self.usado_em is None and agora < self.expira_em

    def marcar_usado(self, agora: datetime) -> "TokenUsoUnico":
        return replace(self, usado_em=agora)

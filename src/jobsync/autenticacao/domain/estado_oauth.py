"""Entidade EstadoOAuth: dados temporários de um login em andamento com um provedor."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from jobsync.autenticacao.domain._instantes import exigir_fuso


@dataclass(frozen=True)
class EstadoOAuth:
    """Guarda o hash do `state` junto do verificador PKCE, do `nonce` e do destino pós-login."""

    estado_hash: bytes
    provedor: str
    code_verifier: str
    nonce: str
    destino: str
    expira_em: datetime

    def __post_init__(self) -> None:
        if not self.estado_hash:
            raise ValueError("O hash do estado não pode ser vazio.")
        for nome in ("provedor", "code_verifier", "nonce", "destino"):
            if not getattr(self, nome).strip():
                raise ValueError(f"O campo {nome} não pode ser vazio.")
        exigir_fuso(self.expira_em)

    @classmethod
    def iniciar(
        cls,
        estado_hash: bytes,
        provedor: str,
        code_verifier: str,
        nonce: str,
        destino: str,
        agora: datetime,
        validade: timedelta,
    ) -> "EstadoOAuth":
        exigir_fuso(agora)
        return cls(estado_hash, provedor, code_verifier, nonce, destino, agora + validade)

    def expirado(self, agora: datetime) -> bool:
        return agora >= self.expira_em

"""Porta do provedor de identidade externo (OpenID Connect)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class IdentidadeAutenticada:
    """Resultado de um login bem-sucedido no provedor."""

    provedor: str
    subject: str
    email: str
    email_verificado: bool
    nome: Optional[str] = None


class ProvedorIdentidade(Protocol):
    nome: str

    def url_autorizacao(self, estado: str, nonce: str, code_challenge: str) -> str: ...

    def trocar_codigo(self, codigo: str, code_verifier: str, nonce: str) -> IdentidadeAutenticada:
        """Levanta `ProvedorIndisponivel` em falha de rede ou resposta/token inválidos."""
        ...

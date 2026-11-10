"""Resultado de um login bem-sucedido: o token (para o cookie) e o usuário."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.autenticacao.domain.usuario import Usuario


@dataclass(frozen=True)
class SessaoIniciada:
    token: str
    usuario: Usuario

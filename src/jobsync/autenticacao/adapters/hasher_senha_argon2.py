"""Adapter de HasherSenha com Argon2id (parâmetros padrão da biblioteca argon2-cffi)."""
from __future__ import annotations

from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError


class HasherSenhaArgon2:
    def __init__(self, hasher: Optional[PasswordHasher] = None) -> None:
        self._hasher = hasher or PasswordHasher()

    def gerar(self, senha: str) -> str:
        return self._hasher.hash(senha)

    def conferir(self, senha: str, senha_hash: str) -> bool:
        try:
            return self._hasher.verify(senha_hash, senha)
        except (VerificationError, InvalidHashError):
            return False

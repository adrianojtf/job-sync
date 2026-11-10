"""Porta de transformação e conferência de senhas."""
from __future__ import annotations

from typing import Protocol


class HasherSenha(Protocol):
    def gerar(self, senha: str) -> str: ...

    def conferir(self, senha: str, senha_hash: str) -> bool: ...

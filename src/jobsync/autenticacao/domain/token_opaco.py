"""Geração e hash de tokens opacos (sessão, confirmação de e-mail, redefinição, `state`)."""
from __future__ import annotations

import hashlib
import secrets

_BYTES_DE_ENTROPIA = 32


def gerar_token() -> str:
    """Token aleatório de 256 bits, seguro para URLs e cookies."""
    return secrets.token_urlsafe(_BYTES_DE_ENTROPIA)


def hash_token(token: str) -> bytes:
    """Só o hash vai ao banco: um vazamento dele não entrega tokens válidos."""
    return hashlib.sha256(token.encode("utf-8")).digest()


def chave_de_limite(prefixo: str, valor: str) -> str:
    """Chave do limite de tentativas sem expor e-mail ou IP em texto puro."""
    return f"{prefixo}:{hashlib.sha256(valor.encode('utf-8')).hexdigest()[:32]}"

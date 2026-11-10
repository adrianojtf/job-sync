"""Validação do destino pós-login, para impedir redirecionamento para outro site."""
from __future__ import annotations

from typing import Optional

DESTINO_PADRAO = "/"
_TAMANHO_MAXIMO = 2048


def destino_seguro(destino: Optional[str]) -> str:
    """Só aceita caminhos internos; qualquer outra coisa vira a raiz."""
    if not destino or len(destino) > _TAMANHO_MAXIMO:
        return DESTINO_PADRAO
    if not destino.startswith("/") or destino.startswith("//") or "\\" in destino:
        return DESTINO_PADRAO
    if any(ord(caractere) < 32 or ord(caractere) == 127 for caractere in destino):
        return DESTINO_PADRAO
    return destino

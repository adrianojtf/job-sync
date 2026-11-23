"""Normalização de texto para comparar frases sem depender de caixa, acento ou pontuação."""
from __future__ import annotations

import re
import unicodedata

_NAO_ALFANUMERICO = re.compile(r"[^a-z0-9]+")


def normalizar_texto(texto: str) -> str:
    """Minúsculas, sem acento e sem pontuação, com espaços simples."""
    sem_acento = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode("ascii")
    return _NAO_ALFANUMERICO.sub(" ", sem_acento).strip()

"""Validação compartilhada dos instantes das entidades de autenticação."""
from __future__ import annotations

from datetime import datetime


def exigir_fuso(*instantes: datetime) -> None:
    if any(instante.tzinfo is None for instante in instantes):
        raise ValueError("Os instantes devem ter fuso horário.")

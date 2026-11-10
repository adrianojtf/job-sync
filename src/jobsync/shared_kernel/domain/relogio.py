"""Relógio do domínio: instantes sempre em UTC, com fuso.

Quem exibe a data aplica o fuso do usuário (o navegador).
"""
from __future__ import annotations

from datetime import datetime, timezone


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)

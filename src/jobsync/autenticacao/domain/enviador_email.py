"""Porta de envio de e-mails transacionais."""
from __future__ import annotations

from typing import Protocol

from jobsync.autenticacao.domain.email import Email


class EnviadorEmail(Protocol):
    def enviar(self, para: Email, assunto: str, corpo: str) -> None: ...

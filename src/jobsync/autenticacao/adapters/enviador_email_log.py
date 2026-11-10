"""Adapter de EnviadorEmail que apenas registra a mensagem em log.

Uso exclusivo em desenvolvimento: o corpo (com o link e o token) vai para o log para que
o fluxo possa ser percorrido sem servidor SMTP. O endereço do destinatário é mascarado.
"""
from __future__ import annotations

import logging

from jobsync.autenticacao.domain.email import Email

logger = logging.getLogger(__name__)


def _mascarar(email: Email) -> str:
    parte_local, dominio = email.valor.split("@", 1)
    return f"{parte_local[:1]}***@{dominio}"


class EnviadorEmailLog:
    def enviar(self, para: Email, assunto: str, corpo: str) -> None:
        logger.info("E-mail (somente log) para %s | %s | %s", _mascarar(para), assunto, corpo)

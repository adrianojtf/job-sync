"""Adapter de EnviadorEmail via SMTP, usando apenas a biblioteca padrão."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import Callable, Optional

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import EnvioEmailFalhou

logger = logging.getLogger(__name__)

_TIMEOUT_SEGUNDOS = 10


class EnviadorEmailSmtp:
    def __init__(
        self,
        host: str,
        porta: int,
        remetente: str,
        usuario: Optional[str] = None,
        senha: Optional[str] = None,
        usar_starttls: bool = True,
        fabrica_smtp: Callable[..., smtplib.SMTP] = smtplib.SMTP,
    ) -> None:
        self._host = host
        self._porta = porta
        self._remetente = remetente
        self._usuario = usuario
        self._senha = senha
        self._usar_starttls = usar_starttls
        self._fabrica_smtp = fabrica_smtp

    def enviar(self, para: Email, assunto: str, corpo: str) -> None:
        mensagem = EmailMessage()
        mensagem["From"] = self._remetente
        mensagem["To"] = para.valor
        mensagem["Subject"] = assunto
        mensagem.set_content(corpo)
        try:
            with self._fabrica_smtp(self._host, self._porta, timeout=_TIMEOUT_SEGUNDOS) as smtp:
                if self._usar_starttls:
                    smtp.starttls()
                if self._usuario:
                    smtp.login(self._usuario, self._senha or "")
                smtp.send_message(mensagem)
        except (smtplib.SMTPException, OSError) as erro:
            logger.error("Falha ao enviar e-mail pelo SMTP: %s", type(erro).__name__)
            raise EnvioEmailFalhou("Não foi possível enviar o e-mail.") from erro

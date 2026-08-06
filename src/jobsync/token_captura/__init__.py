"""Domínio Token de Captura: tokens opacos para autenticar captura de vagas."""

from jobsync.token_captura.domain.token_captura import TokenCaptura
from jobsync.token_captura.domain.token_captura_repository import TokenCapturaRepository

__all__ = ["TokenCaptura", "TokenCapturaRepository"]

"""Caso de uso: resolver perfil por token de captura."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from jobsync.token_captura.domain.token_captura_repository import TokenCapturaRepository


@dataclass
class ResolverPerfilPorToken:
    """Resolve o identificador de perfil a partir de um token de captura."""

    _repositorio: TokenCapturaRepository

    def executar(self, token: str) -> Optional[str]:
        """Retorna o identificador do perfil dono do token, ou None se inválido."""
        return self._repositorio.resolver_perfil_por_token(token)

"""Caso de uso: criar um token de captura para um perfil."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.token_captura.domain.token_captura import TokenCaptura
from jobsync.token_captura.domain.token_captura_repository import TokenCapturaRepository


@dataclass
class CriarTokenCaptura:
    """Gera e persiste um token de captura vinculado a um perfil."""

    _repositorio: TokenCapturaRepository

    def executar(self, perfil_identificador: str) -> TokenCaptura:
        """Cria e retorna um novo token de captura para o perfil informado."""
        return self._repositorio.criar(perfil_identificador)

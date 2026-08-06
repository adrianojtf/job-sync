"""Repository (Port) para persistência e resolução de tokens de captura."""

from abc import ABC, abstractmethod
from typing import Optional

from jobsync.token_captura.domain.token_captura import TokenCaptura


class TokenCapturaRepository(ABC):
    """Interface de domínio para criar tokens de captura e resolver o perfil dono de um token."""

    @abstractmethod
    def criar(self, perfil_identificador: str) -> TokenCaptura:
        """Gera e persiste um novo token de captura para o perfil informado."""
        raise NotImplementedError

    @abstractmethod
    def resolver_perfil_por_token(self, token: str) -> Optional[str]:
        """Retorna o identificador do perfil dono do token, ou None se o token for inválido."""
        raise NotImplementedError

"""Repository (Port) para persistência de perfis de usuário."""

from abc import ABC, abstractmethod
from typing import Optional

from domain.perfil import Perfil


class PerfilRepository(ABC):
    """Interface de domínio para buscar e criar perfis."""

    @abstractmethod
    def buscar_por_identificador(self, identificador: str) -> Optional[Perfil]:
        """Retorna o perfil com o identificador informado, ou None se não existir."""
        raise NotImplementedError

    @abstractmethod
    def criar(self, identificador: str) -> Perfil:
        """Cria e persiste um novo perfil com o identificador informado."""
        raise NotImplementedError

"""Repository (Port) para persistência do Perfil Estruturado."""

from abc import ABC, abstractmethod

from domain.perfil_estruturado import PerfilEstruturado


class PerfilEstruturadoRepository(ABC):
    """Interface de domínio para gerenciar o perfil estruturado de um login."""

    @abstractmethod
    def salvar(self, perfil: PerfilEstruturado) -> PerfilEstruturado:
        """Persiste o perfil (upsert — uma linha por perfil_identificador, sem histórico)."""
        raise NotImplementedError

    @abstractmethod
    def buscar_por_perfil(self, perfil_identificador: str) -> PerfilEstruturado | None:
        """Retorna o perfil estruturado do identificador informado, ou None se não existir."""
        raise NotImplementedError

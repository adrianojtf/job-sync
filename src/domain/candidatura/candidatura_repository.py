"""Repository (Port) para persistência de candidaturas (Kanban)."""

from abc import ABC, abstractmethod

from domain.candidatura import Candidatura, StatusCandidatura


class CandidaturaRepository(ABC):
    """Interface de domínio para gerenciar candidaturas."""

    @abstractmethod
    def salvar(self, candidatura: Candidatura) -> Candidatura:
        """Persiste uma nova candidatura."""
        raise NotImplementedError

    @abstractmethod
    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]:
        """Lista todas as candidaturas do perfil."""
        raise NotImplementedError

    @abstractmethod
    def atualizar_status(self, candidatura_id: str, novo_status: StatusCandidatura) -> Candidatura:
        """Atualiza o status de uma candidatura e retorna a candidatura atualizada."""
        raise NotImplementedError

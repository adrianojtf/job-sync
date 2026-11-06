"""Repository (Port) para persistência de candidaturas (Kanban)."""

from abc import ABC, abstractmethod

from jobsync.candidatura.domain.candidatura import Candidatura, StatusCandidatura


class CandidaturaNaoEncontrada(LookupError):
    """A candidatura informada não existe."""

    def __init__(self, candidatura_id: str) -> None:
        super().__init__(f"Candidatura não encontrada: {candidatura_id}")
        self.candidatura_id = candidatura_id


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
        """Atualiza o status de uma candidatura e retorna a candidatura atualizada.

        Levanta CandidaturaNaoEncontrada se o id não existir.
        """
        raise NotImplementedError

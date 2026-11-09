"""Repository (Port) para persistência de candidaturas (Kanban)."""

from __future__ import annotations

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

    @abstractmethod
    def buscar_por_id(self, candidatura_id: str) -> Candidatura | None:
        """Devolve a candidatura ou None se o id não existir."""
        raise NotImplementedError

    @abstractmethod
    def aplicar_movimento(
        self,
        candidatura_id: str,
        novo_status: StatusCandidatura,
        ids_destino_ordenados: tuple[str, ...],
    ) -> Candidatura:
        """Move a candidatura para `novo_status` e grava a ordem completa da coluna de destino.

        A operação é atômica: se falhar, nada muda. Quando o status muda, a coluna de origem
        é renumerada para não deixar buracos.
        Levanta CandidaturaNaoEncontrada se o id não existir.
        """
        raise NotImplementedError

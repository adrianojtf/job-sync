"""Repository (Port) para persistência de vagas capturadas."""

from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.vaga.domain.vaga import Vaga


class VagaRepository(ABC):
    """Interface de domínio para salvar e listar vagas capturadas."""

    @abstractmethod
    def salvar(self, vaga: Vaga) -> Vaga:
        """Persiste uma nova vaga capturada."""
        raise NotImplementedError

    @abstractmethod
    def listar_nao_convertidas(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        """Lista as vagas do perfil que ainda não viraram candidatura."""
        raise NotImplementedError

    @abstractmethod
    def marcar_como_convertida(self, vaga_id: str) -> None:
        """Marca a vaga como já convertida em candidatura, removendo-a da listagem pendente."""
        raise NotImplementedError

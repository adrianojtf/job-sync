"""Repository (Port) para persistência da biblioteca de currículos salvos por perfil."""

from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.curriculo_salvo.domain.curriculo_salvo import CurriculoSalvo


class CurriculoSalvoRepository(ABC):
    """Interface de domínio para gerenciar currículos salvos de um perfil."""

    @abstractmethod
    def salvar(self, curriculo: CurriculoSalvo) -> CurriculoSalvo:
        """Persiste um novo currículo salvo."""
        raise NotImplementedError

    @abstractmethod
    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        """Lista os currículos salvos do perfil, ordenados por data de upload decrescente."""
        raise NotImplementedError

    @abstractmethod
    def remover(self, curriculo_id: str, perfil_identificador: str) -> None:
        """Remove um currículo salvo, desde que pertença ao perfil informado."""
        raise NotImplementedError

    @abstractmethod
    def contar_por_perfil(self, perfil_identificador: str) -> int:
        """Retorna a quantidade de currículos salvos ativos do perfil."""
        raise NotImplementedError

    @abstractmethod
    def atualizar_pdf(self, curriculo_id: str, perfil_identificador: str, pdf_bytes: bytes) -> bool:
        """Substitui o PDF de um currículo salvo do perfil; devolve False se ele não existir."""
        raise NotImplementedError

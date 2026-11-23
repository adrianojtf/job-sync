"""Repository (Port) para persistência dos currículos adaptados de um perfil."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado


class CurriculoAdaptadoRepository(ABC):
    """Interface de domínio para guardar e recuperar currículos adaptados, sempre por perfil."""

    @abstractmethod
    def salvar(self, curriculo: CurriculoAdaptado) -> CurriculoAdaptado:
        """Persiste o currículo; se o id já existe no perfil, substitui o conteúdo."""
        raise NotImplementedError

    @abstractmethod
    def buscar(self, curriculo_id: str, perfil_identificador: str) -> CurriculoAdaptado | None:
        """Devolve o currículo do perfil, ou None se não existir ou for de outro perfil."""
        raise NotImplementedError

    @abstractmethod
    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoAdaptado, ...]:
        """Lista os currículos do perfil, do atualizado mais recentemente para o mais antigo."""
        raise NotImplementedError

    @abstractmethod
    def vincular_curriculo_salvo(
        self, curriculo_id: str, perfil_identificador: str, curriculo_salvo_id: str
    ) -> None:
        """Guarda o id do currículo salvo (PDF) gerado a partir deste currículo adaptado."""
        raise NotImplementedError

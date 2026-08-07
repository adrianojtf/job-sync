"""Caso de uso: buscar o perfil estruturado de um login, se existir."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.perfil_estruturado.domain.perfil_estruturado import PerfilEstruturado
from jobsync.perfil_estruturado.domain.perfil_estruturado_repository import PerfilEstruturadoRepository


@dataclass
class BuscarPerfilEstruturado:
    """Retorna o perfil estruturado do identificador informado, ou None."""

    repositorio: PerfilEstruturadoRepository

    def executar(self, perfil_identificador: str) -> PerfilEstruturado | None:
        return self.repositorio.buscar_por_perfil(perfil_identificador)

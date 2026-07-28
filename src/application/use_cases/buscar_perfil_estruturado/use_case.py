"""Caso de uso: buscar o perfil estruturado de um login, se existir."""
from __future__ import annotations

from domain.perfil_estruturado import PerfilEstruturado
from domain.perfil_estruturado.perfil_estruturado_repository import PerfilEstruturadoRepository


class BuscarPerfilEstruturado:
    """Retorna o perfil estruturado do identificador informado, ou None."""

    def __init__(self, repositorio: PerfilEstruturadoRepository) -> None:
        self._repositorio = repositorio

    def executar(self, perfil_identificador: str) -> PerfilEstruturado | None:
        return self._repositorio.buscar_por_perfil(perfil_identificador)

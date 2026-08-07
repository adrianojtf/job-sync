"""Implementação em memória (fake) de PerfilEstruturadoRepository para testes."""

from __future__ import annotations

from jobsync.perfil_estruturado.domain.perfil_estruturado import PerfilEstruturado
from jobsync.perfil_estruturado.domain.perfil_estruturado_repository import (
    PerfilEstruturadoRepository,
)


class PerfilEstruturadoRepositoryFake(PerfilEstruturadoRepository):
    """Fake em memória para testes de API e serviços."""

    def __init__(self) -> None:
        self._perfis: dict[str, PerfilEstruturado] = {}

    def salvar(self, perfil: PerfilEstruturado) -> PerfilEstruturado:
        self._perfis[perfil.perfil_identificador] = perfil
        return perfil

    def buscar_por_perfil(self, perfil_identificador: str) -> PerfilEstruturado | None:
        return self._perfis.get(perfil_identificador)

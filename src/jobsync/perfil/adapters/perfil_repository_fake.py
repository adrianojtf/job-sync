"""Implementação em memória (fake) de PerfilRepository para testes."""

from __future__ import annotations

from typing import Optional

from jobsync.perfil.domain.perfil import Perfil
from jobsync.perfil.domain.perfil_repository import PerfilRepository


class PerfilRepositoryFake(PerfilRepository):
    """Fake em memória para testes de API e serviços."""

    def __init__(self) -> None:
        self._perfis: dict[str, Perfil] = {}

    def buscar_por_identificador(self, identificador: str) -> Optional[Perfil]:
        return self._perfis.get(identificador)

    def criar(self, identificador: str) -> Perfil:
        perfil = Perfil(identificador=identificador)
        self._perfis[identificador] = perfil
        return perfil

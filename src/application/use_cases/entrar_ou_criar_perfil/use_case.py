"""Caso de uso: login simples — busca o perfil pelo identificador, criando-o se necessário."""
from __future__ import annotations

from domain.perfil import Perfil
from domain.perfil.perfil_repository import PerfilRepository


class EntrarOuCriarPerfil:
    """Resolve o perfil ativo a partir de um identificador, sem exigir senha."""

    def __init__(self, repositorio_perfil: PerfilRepository) -> None:
        self._repositorio_perfil = repositorio_perfil

    def executar(self, identificador: str) -> Perfil:
        perfil_existente = self._repositorio_perfil.buscar_por_identificador(identificador)
        if perfil_existente is not None:
            return perfil_existente
        return self._repositorio_perfil.criar(identificador)

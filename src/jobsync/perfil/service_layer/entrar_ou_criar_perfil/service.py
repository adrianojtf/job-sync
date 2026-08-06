"""Caso de uso: login simples — busca o perfil pelo identificador, criando-o se necessário."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.perfil.domain.perfil import Perfil
from jobsync.perfil.domain.perfil_repository import PerfilRepository


@dataclass
class EntrarOuCriarPerfil:
    """Resolve o perfil ativo a partir de um identificador, sem exigir senha."""

    _repositorio_perfil: PerfilRepository

    def executar(self, identificador: str) -> Perfil:
        perfil_existente = self._repositorio_perfil.buscar_por_identificador(identificador)
        if perfil_existente is not None:
            return perfil_existente
        return self._repositorio_perfil.criar(identificador)

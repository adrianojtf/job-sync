"""Caso de uso: listar as vagas capturadas de um perfil ainda não convertidas em candidatura."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.vaga.domain.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository


@dataclass
class ListarVagasCapturadas:
    """Lista as vagas capturadas do perfil que ainda não viraram candidatura."""

    _repositorio_vaga: VagaRepository

    def executar(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        return self._repositorio_vaga.listar_nao_convertidas(perfil_identificador)

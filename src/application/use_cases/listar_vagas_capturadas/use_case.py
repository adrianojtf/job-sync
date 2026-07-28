"""Caso de uso: listar as vagas capturadas de um perfil ainda não convertidas em candidatura."""
from __future__ import annotations

from domain.vaga import Vaga
from domain.vaga.vaga_repository import VagaRepository


class ListarVagasCapturadas:
    """Lista as vagas capturadas do perfil que ainda não viraram candidatura."""

    def __init__(self, repositorio_vaga: VagaRepository) -> None:
        self._repositorio_vaga = repositorio_vaga

    def executar(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        return self._repositorio_vaga.listar_nao_convertidas(perfil_identificador)

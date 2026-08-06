"""Caso de uso: remover um currículo salvo, validando que pertence ao perfil informado."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.curriculo_salvo.domain.curriculo_salvo_repository import CurriculoSalvoRepository


class CurriculoSalvoNaoEncontrado(ValueError):
    """Levantado quando o currículo informado não pertence ao perfil informado."""


@dataclass
class RemoverCurriculoSalvo:
    """Remove um currículo salvo, impedindo a remoção de currículos de outro perfil."""

    _repositorio_curriculo_salvo: CurriculoSalvoRepository

    def executar(self, curriculo_id: str, perfil_identificador: str) -> None:
        curriculos_do_perfil = self._repositorio_curriculo_salvo.listar_por_perfil(perfil_identificador)
        pertence_ao_perfil = any(c.id == curriculo_id for c in curriculos_do_perfil)
        if not pertence_ao_perfil:
            raise CurriculoSalvoNaoEncontrado(
                f"Currículo '{curriculo_id}' não encontrado para este perfil."
            )
        self._repositorio_curriculo_salvo.remover(curriculo_id, perfil_identificador)

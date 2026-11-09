"""Porta para apontar tecnologias do perfil equivalentes às pedidas pela vaga."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.equivalencia_tecnologia import EquivalenciaTecnologia


class IdentificadorEquivalenciasPort(ABC):
    """Aponta pares (tecnologia do perfil → tecnologia da vaga) da mesma categoria.

    Só aponta os pares; em quais experiências a troca acontece é decidido pelo
    `PlanoAdaptacao`, no domínio.
    """

    @abstractmethod
    def identificar(
        self,
        experiencias: Sequence[ExperienciaParaAvaliacao],
        contexto: ContextoVaga,
    ) -> tuple[EquivalenciaTecnologia, ...]:
        raise NotImplementedError

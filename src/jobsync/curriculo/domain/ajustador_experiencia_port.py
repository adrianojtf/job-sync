"""Porta para adaptar individualmente uma experiência profissional a uma vaga."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.equivalencia_tecnologia import DiretrizesExperiencia
from jobsync.curriculo.domain.experiencia_adaptada import ExperienciaAdaptada


class AjustadorExperienciaPort(ABC):
    """Contrato para escrever uma experiência no padrão conquistas + contexto.

    Cargo, empresa e período do resultado são sempre os da experiência recebida.
    """

    @abstractmethod
    def ajustar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        contexto: ContextoVaga,
        diretrizes: DiretrizesExperiencia,
    ) -> ExperienciaAdaptada:
        """Adapta a descrição em texto livre do perfil para a vaga, seguindo as trocas e
        manutenções de tecnologia definidas para esta experiência."""
        raise NotImplementedError

    @abstractmethod
    def refinar(self, experiencia: ExperienciaAdaptada, contexto: ContextoVaga) -> ExperienciaAdaptada:
        """Reescreve conquistas e contexto já adaptados, partindo do texto atual do usuário."""
        raise NotImplementedError

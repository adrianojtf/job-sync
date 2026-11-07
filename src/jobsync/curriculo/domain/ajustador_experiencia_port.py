"""Porta para adaptar individualmente uma experiência profissional a uma vaga."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.experiencia_adaptada import ExperienciaAdaptada
from jobsync.vaga.domain.analise_vaga import AnaliseVaga


class AjustadorExperienciaPort(ABC):
    """Contrato para escrever uma experiência no padrão conquistas + contexto.

    Cargo, empresa e período do resultado são sempre os da experiência recebida.
    """

    @abstractmethod
    def ajustar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> ExperienciaAdaptada:
        """Adapta a descrição em texto livre do perfil para a vaga."""
        raise NotImplementedError

    @abstractmethod
    def refinar(
        self,
        experiencia: ExperienciaAdaptada,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> ExperienciaAdaptada:
        """Reescreve conquistas e contexto já adaptados, partindo do texto atual do usuário."""
        raise NotImplementedError

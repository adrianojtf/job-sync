"""Porta para a IA completar os blocos ausentes de uma experiência."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.perfil_estruturado.domain.blocos_experiencia import BlocosExperiencia, ExperienciaParaCompletar


class CompletadorBlocosExperienciaPort(ABC):
    """Gera só os blocos ausentes de uma experiência, sem alterar os reconhecidos."""

    @abstractmethod
    def completar(self, experiencia: ExperienciaParaCompletar, idioma: str | None = None) -> BlocosExperiencia:
        """Devolve os blocos gerados para os que faltam em `experiencia.reconhecidos`.

        `idioma` é "pt" ou "en"; sem ele, a IA escreve no mesmo idioma do texto de origem.
        Levanta `CompletarBlocosIndisponivel` quando não consegue gerar um resultado utilizável.
        """
        raise NotImplementedError

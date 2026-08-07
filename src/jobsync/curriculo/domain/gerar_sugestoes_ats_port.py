"""Porta (Port) para geração de sugestões de melhoria de ATS Score."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jobsync.ats_score import ResultadoAtsScore
    from jobsync.curriculo import Curriculo
    from jobsync.vaga import AnaliseVaga


class GerarSugestoesAtsPort(ABC):
    """Interface da porta de aplicação para sugerir mudanças que aumentem o ATS Score."""

    @abstractmethod
    def gerar(
        self,
        curriculo: "Curriculo",
        analise_vaga: "AnaliseVaga",
        resultado_ats: "ResultadoAtsScore",
    ) -> tuple[str, ...]:
        """Gera sugestões acionáveis (uma por tópico) de como aumentar a aderência à vaga.

        A implementação concreta deve se ater aos requisitos faltantes já
        identificados em `resultado_ats` e ao conteúdo real do currículo,
        sem sugerir que o candidato afirme ter experiência que não possui.
        """
        raise NotImplementedError

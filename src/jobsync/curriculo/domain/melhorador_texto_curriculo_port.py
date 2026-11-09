"""Porta para melhorar a escrita de um trecho do currículo, sem vaga-alvo."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.curriculo import SecaoCurriculo
from jobsync.curriculo.domain.refino import PedidoRefino


class MelhoradorTextoCurriculoPort(ABC):
    """Melhora clareza, objetividade e verbos de ação, mantendo idioma e fatos do texto.

    Usada onde não há vaga para orientar o ajuste (tela de cadastro do currículo mestre).
    Parte do texto atual e segue o foco sem vaga da tentativa (JOB-0037).
    """

    @abstractmethod
    def melhorar_secao(self, secao: SecaoCurriculo, refino: PedidoRefino) -> SecaoCurriculo:
        """Retorna a seção com o conteúdo reescrito, preservando tipo e título."""
        raise NotImplementedError

    @abstractmethod
    def melhorar_experiencia(
        self, experiencia: ExperienciaParaAvaliacao, refino: PedidoRefino
    ) -> ExperienciaParaAvaliacao:
        """Retorna a experiência com a descrição reescrita, preservando cargo, empresa e período."""
        raise NotImplementedError

"""Porta para ler os dados de uma vaga a partir do link."""

from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.vaga.domain.dados_vaga import DadosVaga
from jobsync.vaga.domain.link_vaga import LinkVaga


class LeitorVagaPorLinkPort(ABC):
    """Lê a vaga indicada por um link e devolve seus dados como rascunho."""

    @abstractmethod
    def ler(self, link: LinkVaga) -> DadosVaga:
        """Devolve os dados da vaga.

        Levanta `LeituraVagaIndisponivel` quando a vaga não pode ser lida
        (bloqueio, vaga encerrada, página sem dados, tempo esgotado).
        """
        raise NotImplementedError

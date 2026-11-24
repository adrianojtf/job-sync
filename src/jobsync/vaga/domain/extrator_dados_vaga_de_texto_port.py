"""Porta para extrair os dados de uma vaga a partir do texto da descrição."""

from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.vaga.domain.dados_vaga import DadosVaga


class ExtratorDadosVagaDeTextoPort(ABC):
    """Identifica cargo, empresa, local e demais dados em um texto de vaga."""

    @abstractmethod
    def extrair(self, texto: str) -> DadosVaga:
        """Devolve os dados da vaga, mantendo a descrição original sem resumo."""
        raise NotImplementedError

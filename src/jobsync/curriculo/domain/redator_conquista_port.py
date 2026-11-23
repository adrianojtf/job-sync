"""Porta para redigir uma conquista a partir do caso que o candidato descreveu."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.curriculo.domain.lacuna_da_vaga import LacunaDaVaga


class RedatorConquistaPort(ABC):
    """Contrato para transformar a resposta do candidato em uma conquista de currículo."""

    @abstractmethod
    def redigir(self, lacuna: LacunaDaVaga, caso: str, cargo: str, idioma_alvo: str) -> str:
        """Escreve a conquista usando somente o que o candidato informou no caso."""
        raise NotImplementedError

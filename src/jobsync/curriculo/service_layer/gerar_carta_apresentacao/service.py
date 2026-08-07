"""Caso de uso: gerar a carta de apresentação personalizada para uma candidatura."""
from __future__ import annotations

from jobsync.curriculo import Curriculo
from jobsync.curriculo.domain.gerar_carta_apresentacao_port import GerarCartaApresentacaoPort
from jobsync.vaga import AnaliseVaga


class GerarCartaApresentacao:
    """Orquestra a geração da carta de apresentação através da porta correspondente."""

    def __init__(self, gerador_carta: GerarCartaApresentacaoPort) -> None:
        self._gerador_carta = gerador_carta

    def executar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, idioma_alvo: str) -> str:
        return self._gerador_carta.gerar(curriculo, analise_vaga, idioma_alvo)

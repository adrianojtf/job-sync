"""Caso de uso: gerar a carta de apresentação personalizada para uma candidatura."""
from __future__ import annotations

from domain.curriculo import Curriculo
from domain.curriculo.gerar_carta_apresentacao_port import GerarCartaApresentacaoPort
from domain.vaga import AnaliseVaga


class GerarCartaApresentacao:
    """Orquestra a geração da carta de apresentação através da porta correspondente."""

    def __init__(self, gerador_carta: GerarCartaApresentacaoPort) -> None:
        self._gerador_carta = gerador_carta

    def executar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, idioma_alvo: str) -> str:
        return self._gerador_carta.gerar(curriculo, analise_vaga, idioma_alvo)

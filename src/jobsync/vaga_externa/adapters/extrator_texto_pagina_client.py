"""Adapter de extração de texto principal de uma página web via requisição HTTP simples.

Heurística genérica equivalente à usada em `content.js` da extensão de
captura, mas em Python, do lado do servidor: concatena o texto de
parágrafos e cabeçalhos, descartando script/style/nav/footer.
"""
from __future__ import annotations

import logging

import httpx
from bs4 import BeautifulSoup

from jobsync.vaga_externa.domain.extrator_texto_pagina_port import ExtratorTextoPaginaPort

logger = logging.getLogger(__name__)

_TAGS_IGNORADAS = ("script", "style", "nav", "footer", "header", "noscript")
_TAMANHO_MINIMO_TEXTO = 100


class ExtratorTextoPaginaClient(ExtratorTextoPaginaPort):
    """Busca a página via HTTP simples e extrai o texto principal com BeautifulSoup."""

    def __init__(self, timeout_segundos: float = 10.0) -> None:
        self._timeout_segundos = timeout_segundos

    def extrair(self, url: str) -> str | None:
        try:
            resposta = httpx.get(
                url,
                timeout=self._timeout_segundos,
                follow_redirects=True,
                headers={"User-Agent": "job-sync/1.0"},
            )
            resposta.raise_for_status()
        except httpx.HTTPError as erro:
            logger.warning("Falha ao extrair texto da página %s: %s", url, erro)
            return None

        soup = BeautifulSoup(resposta.text, "html.parser")
        for tag in soup(_TAGS_IGNORADAS):
            tag.decompose()

        texto = " ".join(soup.get_text(separator=" ").split())
        if len(texto) < _TAMANHO_MINIMO_TEXTO:
            return None
        return texto

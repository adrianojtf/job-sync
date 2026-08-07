"""Adapter de busca de vagas no feed RSS público da We Work Remotely.

A fonte não oferece busca por query string — o feed inteiro é consultado e o
filtro pelo termo é feito localmente (título ou descrição).
"""
from __future__ import annotations

import logging
from datetime import date, datetime

import feedparser
import httpx

from jobsync.vaga_externa.domain.buscador_vagas_externo_port import BuscadorVagasExternoPort
from jobsync.vaga_externa.domain.vaga_externa import FonteVagaExterna, VagaExterna

logger = logging.getLogger(__name__)


def _parsear_data(entrada: object) -> date | None:
    struct_time = getattr(entrada, "published_parsed", None)
    if not struct_time:
        return None
    try:
        return datetime(*struct_time[:6]).date()
    except (TypeError, ValueError):
        return None


class BuscadorWeWorkRemotelyClient(BuscadorVagasExternoPort):
    """Consulta o feed RSS de vagas remotas de programação da We Work Remotely."""

    _URL_FEED = "https://weworkremotely.com/categories/remote-programming-jobs.rss"

    def __init__(self, timeout_segundos: float = 8.0) -> None:
        self._timeout_segundos = timeout_segundos

    def buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]:
        try:
            resposta = httpx.get(self._URL_FEED, timeout=self._timeout_segundos)
            resposta.raise_for_status()
        except httpx.HTTPError as erro:
            logger.warning("Falha ao buscar vagas na We Work Remotely: %s", erro)
            return ()

        feed = feedparser.parse(resposta.content)
        termo_lower = termo.lower()

        vagas = []
        for entrada in feed.entries:
            titulo_bruto = str(getattr(entrada, "title", "") or "")
            descricao = str(getattr(entrada, "summary", "") or titulo_bruto)
            if termo_lower not in titulo_bruto.lower() and termo_lower not in descricao.lower():
                continue

            if ":" in titulo_bruto:
                empresa, titulo = titulo_bruto.split(":", 1)
            else:
                empresa, titulo = "Não informado", titulo_bruto

            vagas.append(
                VagaExterna(
                    titulo=titulo.strip() or titulo_bruto,
                    empresa=empresa.strip(),
                    descricao=descricao,
                    url=str(getattr(entrada, "link", "")),
                    fonte=FonteVagaExterna.WE_WORK_REMOTELY,
                    data_publicacao=_parsear_data(entrada),
                )
            )
        return tuple(vagas)

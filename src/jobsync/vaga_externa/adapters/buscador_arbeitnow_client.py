"""Adapter de busca de vagas na API pública do Arbeitnow."""
from __future__ import annotations

import logging
from datetime import date, datetime, timezone

import httpx

from jobsync.vaga_externa.domain.buscador_vagas_externo_port import BuscadorVagasExternoPort
from jobsync.vaga_externa.domain.vaga_externa import FonteVagaExterna, VagaExterna

logger = logging.getLogger(__name__)


def _parsear_data(valor: object) -> date | None:
    if valor is None:
        return None
    try:
        return datetime.fromtimestamp(float(valor), tz=timezone.utc).date()
    except (TypeError, ValueError, OSError):
        return None


class BuscadorArbeitnowClient(BuscadorVagasExternoPort):
    """Consulta `GET https://www.arbeitnow.com/api/job-board-api?search={termo}`, sem autenticação."""

    _URL_BASE = "https://www.arbeitnow.com/api/job-board-api"

    def __init__(self, timeout_segundos: float = 8.0) -> None:
        self._timeout_segundos = timeout_segundos

    def buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]:
        try:
            resposta = httpx.get(
                self._URL_BASE,
                params={"search": termo},
                timeout=self._timeout_segundos,
            )
            resposta.raise_for_status()
            dados = resposta.json()
        except (httpx.HTTPError, ValueError) as erro:
            logger.warning("Falha ao buscar vagas na Arbeitnow: %s", erro)
            return ()

        vagas = []
        for item in dados.get("data", []):
            if not isinstance(item, dict) or not item.get("title"):
                continue
            vagas.append(
                VagaExterna(
                    titulo=str(item["title"]),
                    empresa=str(item.get("company_name") or "Não informado"),
                    descricao=str(item.get("description") or item["title"]),
                    url=str(item.get("url") or ""),
                    fonte=FonteVagaExterna.ARBEITNOW,
                    data_publicacao=_parsear_data(item.get("created_at")),
                )
            )
        return tuple(vagas)

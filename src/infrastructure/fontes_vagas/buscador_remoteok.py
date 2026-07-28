"""Adapter de busca de vagas na API pública do RemoteOK."""
from __future__ import annotations

import logging
from datetime import date, datetime

import httpx

from domain.vaga_externa import FonteVagaExterna, VagaExterna
from domain.vaga_externa.buscador_vagas_externo_port import BuscadorVagasExternoPort

logger = logging.getLogger(__name__)


def _parsear_data(valor: object) -> date | None:
    if not valor:
        return None
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00")).date()
    except ValueError:
        return None


class BuscadorRemoteOk(BuscadorVagasExternoPort):
    """Consulta `GET https://remoteok.com/api?search={termo}`, sem autenticação."""

    _URL_BASE = "https://remoteok.com/api"

    def __init__(self, timeout_segundos: float = 8.0) -> None:
        self._timeout_segundos = timeout_segundos

    def buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]:
        try:
            resposta = httpx.get(
                self._URL_BASE,
                params={"search": termo},
                timeout=self._timeout_segundos,
                headers={"User-Agent": "job-sync/1.0"},
            )
            resposta.raise_for_status()
            dados = resposta.json()
        except (httpx.HTTPError, ValueError) as erro:
            logger.warning("Falha ao buscar vagas no RemoteOK: %s", erro)
            return ()

        vagas = []
        for item in dados:
            if not isinstance(item, dict) or not item.get("position"):
                continue
            vagas.append(
                VagaExterna(
                    titulo=str(item["position"]),
                    empresa=str(item.get("company") or "Não informado"),
                    descricao=str(item.get("description") or item["position"]),
                    url=str(item.get("url") or f"https://remoteok.com/remote-jobs/{item.get('id', '')}"),
                    fonte=FonteVagaExterna.REMOTEOK,
                    data_publicacao=_parsear_data(item.get("date")),
                )
            )
        return tuple(vagas)

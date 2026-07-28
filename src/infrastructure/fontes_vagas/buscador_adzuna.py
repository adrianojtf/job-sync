"""Adapter de busca de vagas na API da Adzuna (credenciais gratuitas via cadastro)."""
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


class BuscadorAdzuna(BuscadorVagasExternoPort):
    """Consulta `GET https://api.adzuna.com/v1/api/jobs/{pais}/search/1`, com `app_id`/`app_key`."""

    def __init__(
        self,
        app_id: str,
        app_key: str,
        pais: str = "gb",
        timeout_segundos: float = 8.0,
    ) -> None:
        self._app_id = app_id
        self._app_key = app_key
        self._pais = pais
        self._timeout_segundos = timeout_segundos

    def buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]:
        url = f"https://api.adzuna.com/v1/api/jobs/{self._pais}/search/1"
        params = {
            "app_id": self._app_id,
            "app_key": self._app_key,
            "what": termo,
        }
        if dias_maximo is not None:
            params["max_days_old"] = dias_maximo
        try:
            resposta = httpx.get(url, params=params, timeout=self._timeout_segundos)
            resposta.raise_for_status()
            dados = resposta.json()
        except (httpx.HTTPError, ValueError) as erro:
            logger.warning("Falha ao buscar vagas na Adzuna: %s", erro)
            return ()

        vagas = []
        for item in dados.get("results", []):
            if not isinstance(item, dict) or not item.get("title"):
                continue
            empresa = (item.get("company") or {}).get("display_name") or "Não informado"
            vagas.append(
                VagaExterna(
                    titulo=str(item["title"]),
                    empresa=str(empresa),
                    descricao=str(item.get("description") or item["title"]),
                    url=str(item.get("redirect_url") or ""),
                    fonte=FonteVagaExterna.ADZUNA,
                    data_publicacao=_parsear_data(item.get("created")),
                )
            )
        return tuple(vagas)

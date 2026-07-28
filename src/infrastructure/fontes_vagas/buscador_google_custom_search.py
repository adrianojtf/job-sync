"""Adapter de busca de vagas via Google Custom Search JSON API (API oficial).

Diferente das demais fontes, só devolve link + snippet — busca a página de
origem via `ExtratorTextoPaginaPort` para obter a descrição completa, com
fallback gracioso para o snippet quando a extração falha.
"""
from __future__ import annotations

import logging

import httpx

from domain.vaga_externa import FonteVagaExterna, VagaExterna
from domain.vaga_externa.buscador_vagas_externo_port import BuscadorVagasExternoPort
from domain.vaga_externa.extrator_texto_pagina_port import ExtratorTextoPaginaPort

logger = logging.getLogger(__name__)

_HTTP_COTA_ESGOTADA = 429


class BuscadorGoogleCustomSearch(BuscadorVagasExternoPort):
    """Consulta `GET https://www.googleapis.com/customsearch/v1`, com `api_key`/`cx`."""

    _URL_BASE = "https://www.googleapis.com/customsearch/v1"

    def __init__(
        self,
        api_key: str,
        search_engine_id: str,
        extrator_texto_pagina: ExtratorTextoPaginaPort,
        timeout_segundos: float = 15.0,
    ) -> None:
        self._api_key = api_key
        self._search_engine_id = search_engine_id
        self._extrator_texto_pagina = extrator_texto_pagina
        self._timeout_segundos = timeout_segundos

    def buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]:
        # dias_maximo é ignorado: a API não expõe data de publicação da vaga
        # (só de indexação da página), então data_publicacao fica sempre None.
        try:
            resposta = httpx.get(
                self._URL_BASE,
                params={"key": self._api_key, "cx": self._search_engine_id, "q": termo},
                timeout=self._timeout_segundos,
            )
            if resposta.status_code == _HTTP_COTA_ESGOTADA:
                logger.warning("Cota diária da Google Custom Search API esgotada.")
                return ()
            resposta.raise_for_status()
            dados = resposta.json()
        except (httpx.HTTPError, ValueError) as erro:
            logger.warning("Falha ao buscar vagas na Google Custom Search: %s", erro)
            return ()

        vagas = []
        for item in dados.get("items", []):
            if not isinstance(item, dict) or not item.get("title") or not item.get("link"):
                continue

            url = str(item["link"])
            descricao_completa = self._extrator_texto_pagina.extrair(url)
            descricao_incompleta = descricao_completa is None
            descricao = descricao_completa or str(item.get("snippet") or item["title"])

            vagas.append(
                VagaExterna(
                    titulo=str(item["title"]),
                    empresa=str(item.get("displayLink") or "Não informado"),
                    descricao=descricao,
                    url=url,
                    fonte=FonteVagaExterna.GOOGLE_CUSTOM_SEARCH,
                    descricao_incompleta=descricao_incompleta,
                )
            )
        return tuple(vagas)

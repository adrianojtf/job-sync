"""Adapters concretos do domínio Vaga Externa."""

from jobsync.vaga_externa.adapters.buscador_adzuna_client import BuscadorAdzunaClient
from jobsync.vaga_externa.adapters.buscador_arbeitnow_client import BuscadorArbeitnowClient
from jobsync.vaga_externa.adapters.buscador_google_custom_search_client import (
    BuscadorGoogleCustomSearchClient,
)
from jobsync.vaga_externa.adapters.buscador_remoteok_client import BuscadorRemoteOkClient
from jobsync.vaga_externa.adapters.buscador_wwr_client import BuscadorWeWorkRemotelyClient
from jobsync.vaga_externa.adapters.extrator_texto_pagina_client import ExtratorTextoPaginaClient

__all__ = [
    "BuscadorAdzunaClient",
    "BuscadorArbeitnowClient",
    "BuscadorGoogleCustomSearchClient",
    "BuscadorRemoteOkClient",
    "BuscadorWeWorkRemotelyClient",
    "ExtratorTextoPaginaClient",
]

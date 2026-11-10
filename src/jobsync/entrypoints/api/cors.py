"""Configuração de CORS da API a partir da variável de ambiente CORS_ORIGINS."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_CURINGA = "*"


def obter_origens_cors() -> list[str]:
    """Lê CORS_ORIGINS (lista separada por vírgula). Sem valor, libera todas as origens."""
    valor = os.getenv("CORS_ORIGINS", "")
    origens = [origem.strip() for origem in valor.split(",") if origem.strip()]
    return origens or [_CURINGA]


def configurar_cors(app: FastAPI, origens: list[str]) -> None:
    """Registra o middleware de CORS.

    Credenciais (cookie de sessão) só são aceitas com origens explícitas; com o curinga o
    navegador nunca as envia entre origens, que é o comportamento seguro.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origens,
        allow_credentials=_CURINGA not in origens,
        allow_methods=["*"],
        allow_headers=["*"],
    )

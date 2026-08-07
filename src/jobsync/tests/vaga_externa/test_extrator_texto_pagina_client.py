"""Testes do adapter ExtratorTextoPaginaClient."""

import httpx

from jobsync.vaga_externa.adapters import ExtratorTextoPaginaClient


def test_extrai_texto_principal_de_pagina_html(monkeypatch):
    html = (
        "<html><body>"
        "<p>Este é um parágrafo com conteúdo suficiente para passar do limite mínimo de "
        "caracteres exigido pelo extrator e garantir que o texto principal seja retornado.</p>"
        "<script>var x = 1;</script>"
        "<footer>rodapé</footer>"
        "</body></html>"
    )
    request = httpx.Request("GET", "https://example.com/job")
    monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(200, text=html, request=request))

    texto = ExtratorTextoPaginaClient().extrair("https://example.com/job")

    assert "parágrafo" in texto
    assert "rodapé" not in texto
    assert "<script>" not in texto
    assert len(texto) >= 100


def test_retorna_none_quando_pagina_muito_curta(monkeypatch):
    html = "<html><body><p>curto</p></body></html>"
    request = httpx.Request("GET", "https://example.com/job")
    monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(200, text=html, request=request))

    assert ExtratorTextoPaginaClient().extrair("https://example.com/job") is None


def test_retorna_none_quando_rede_falha(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectError("timeout")))

    assert ExtratorTextoPaginaClient().extrair("https://example.com/job") is None

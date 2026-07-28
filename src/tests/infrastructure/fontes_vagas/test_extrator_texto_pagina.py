"""Testes do adapter ExtratorTextoPagina."""

import httpx

from infrastructure.fontes_vagas.extrator_texto_pagina import ExtratorTextoPagina

_REQUEST_FAKE = httpx.Request("GET", "https://exemplo.com/vaga/1")

_HTML_COM_CONTEUDO = """
<html>
<head><script>console.log('ignorar');</script></head>
<body>
<nav>menu ignorado</nav>
<main>
<h1>Engenheiro de Software Backend</h1>
<p>Vaga remota para engenheiro backend com Python, requisitos: Python, Django, PostgreSQL.</p>
<p>Buscamos alguém com experiência em sistemas distribuídos e testes automatizados.</p>
</main>
<footer>rodapé ignorado</footer>
</body>
</html>
"""

_HTML_CURTO = "<html><body><p>Vazio.</p></body></html>"


class TestExtratorTextoPagina:
    def test_extrai_texto_principal_ignorando_script_nav_footer(self, monkeypatch):
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, text=_HTML_COM_CONTEUDO, request=_REQUEST_FAKE)
        )

        texto = ExtratorTextoPagina().extrair("https://exemplo.com/vaga/1")

        assert texto is not None
        assert "Engenheiro de Software Backend" in texto
        assert "menu ignorado" not in texto
        assert "rodapé ignorado" not in texto
        assert "console.log" not in texto

    def test_pagina_com_pouco_conteudo_retorna_none(self, monkeypatch):
        monkeypatch.setattr(
            httpx, "get", lambda *a, **k: httpx.Response(200, text=_HTML_CURTO, request=_REQUEST_FAKE)
        )

        assert ExtratorTextoPagina().extrair("https://exemplo.com/vaga/2") is None

    def test_erro_de_rede_retorna_none(self, monkeypatch):
        def levantar_erro(*args, **kwargs):
            raise httpx.ConnectTimeout("timeout")

        monkeypatch.setattr(httpx, "get", levantar_erro)

        assert ExtratorTextoPagina().extrair("https://exemplo.com/vaga/3") is None

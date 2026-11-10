import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.cors import configurar_cors, obter_origens_cors


def _client_com_cors(origens: list[str]) -> TestClient:
    app = FastAPI()
    configurar_cors(app, origens)

    @app.get("/ping")
    def ping() -> dict:
        return {"ok": True}

    return TestClient(app)


class TestObterOrigensCors:
    def test_sem_variavel_retorna_curinga(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)

        assert obter_origens_cors() == ["*"]

    def test_lista_separada_por_virgula(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173, https://app.jobsync.com ,")

        assert obter_origens_cors() == ["http://localhost:5173", "https://app.jobsync.com"]

    def test_variavel_vazia_retorna_curinga(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("CORS_ORIGINS", " ")

        assert obter_origens_cors() == ["*"]


class TestConfigurarCors:
    def test_origem_permitida_recebe_cabecalho(self):
        client = _client_com_cors(["http://localhost:5173"])

        response = client.get("/ping", headers={"Origin": "http://localhost:5173"})

        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

    def test_origem_nao_listada_nao_recebe_cabecalho(self):
        client = _client_com_cors(["http://localhost:5173"])

        response = client.get("/ping", headers={"Origin": "https://malicioso.example"})

        assert "access-control-allow-origin" not in response.headers

    def test_origens_explicitas_permitem_credenciais_para_o_cookie_de_sessao(self):
        client = _client_com_cors(["http://localhost:5173"])

        response = client.options(
            "/ping",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.headers["access-control-allow-credentials"] == "true"

    def test_curinga_nao_permite_credenciais(self):
        client = _client_com_cors(["*"])

        response = client.options(
            "/ping",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert "access-control-allow-credentials" not in response.headers

"""Testes da checagem de origem em requisições de escrita com cookie de sessão."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.protecao_csrf import adicionar_protecao_csrf
from jobsync.entrypoints.autenticacao_config import ConfiguracaoHttpAutenticacao

CONFIG = ConfiguracaoHttpAutenticacao(origens_permitidas=("http://localhost:8080", "http://localhost:5173"))


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    adicionar_protecao_csrf(app, lambda: CONFIG)

    @app.post("/escrita")
    def escrita() -> dict:
        return {"ok": True}

    @app.get("/leitura")
    def leitura() -> dict:
        return {"ok": True}

    return TestClient(app, base_url="http://localhost:8080", cookies={"js_sessao": "abc"})


class TestProtecaoCsrf:
    def test_origem_estranha_com_cookie_de_sessao_e_recusada(self, client):
        resposta = client.post("/escrita", headers={"Origin": "https://evil.example.com"})

        assert resposta.status_code == 403
        assert resposta.json()["type"].endswith("/origem-nao-permitida")

    def test_origem_nula_e_recusada(self, client):
        assert client.post("/escrita", headers={"Origin": "null"}).status_code == 403

    @pytest.mark.parametrize("origem", ["http://localhost:8080", "http://localhost:5173"])
    def test_origens_listadas_passam(self, client, origem):
        assert client.post("/escrita", headers={"Origin": origem}).status_code == 200

    def test_mesma_origem_do_host_passa(self, client):
        assert client.post("/escrita", headers={"Origin": "http://localhost:8080"}).status_code == 200

    def test_requisicao_sem_origem_passa(self, client):
        assert client.post("/escrita").status_code == 200

    def test_sem_origem_usa_o_referer(self, client):
        resposta = client.post("/escrita", headers={"Referer": "https://evil.example.com/pagina"})

        assert resposta.status_code == 403

    def test_referer_permitido_passa(self, client):
        assert client.post("/escrita", headers={"Referer": "http://localhost:8080/vagas"}).status_code == 200

    def test_sem_cookie_de_sessao_a_origem_nao_importa(self, client):
        client.cookies.clear()

        resposta = client.post("/escrita", headers={"Origin": "chrome-extension://abcdef"})

        assert resposta.status_code == 200

    def test_metodo_seguro_nao_e_verificado(self, client):
        assert client.get("/leitura", headers={"Origin": "https://evil.example.com"}).status_code == 200

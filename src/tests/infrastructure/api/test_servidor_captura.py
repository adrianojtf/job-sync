"""Testes de serviço do ServidorCaptura (FastAPI), usando TestClient."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from infrastructure.api.servidor_captura import app
from infrastructure.persistence.perfil_repository_impl import PerfilRepositoryImpl
from infrastructure.persistence.token_captura_repository_impl import TokenCapturaRepositoryImpl


@pytest.fixture
def caminho_banco():
    fd, caminho = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield caminho
    os.remove(caminho)


@pytest.fixture
def token_valido(caminho_banco):
    PerfilRepositoryImpl(caminho_banco=caminho_banco).criar("matheus")
    token = TokenCapturaRepositoryImpl(caminho_banco=caminho_banco).criar("matheus")
    return token.token


@pytest.fixture
def client(caminho_banco, monkeypatch):
    monkeypatch.setenv("JOB_SYNC_DB_PATH", caminho_banco)
    return TestClient(app)


class TestServidorCaptura:
    def test_captura_com_token_valido_retorna_201_e_persiste_vaga(self, client, token_valido, caminho_banco):
        resposta = client.post(
            "/api/vagas/capturar",
            json={"texto": "Vaga para Engenheiro de Software", "url": "https://exemplo.com/vaga/1"},
            headers={"Authorization": f"Bearer {token_valido}"},
        )

        assert resposta.status_code == 201
        vaga_id = resposta.json()["id"]
        assert vaga_id

        repo_token = TokenCapturaRepositoryImpl(caminho_banco=caminho_banco)
        assert repo_token.resolver_perfil_por_token(token_valido) == "matheus"

    def test_captura_com_token_invalido_retorna_401(self, client):
        resposta = client.post(
            "/api/vagas/capturar",
            json={"texto": "Vaga qualquer"},
            headers={"Authorization": "Bearer token-que-nao-existe"},
        )

        assert resposta.status_code == 401

    def test_captura_sem_texto_retorna_422(self, client, token_valido):
        resposta = client.post(
            "/api/vagas/capturar",
            json={"url": "https://exemplo.com/vaga/1"},
            headers={"Authorization": f"Bearer {token_valido}"},
        )

        assert resposta.status_code == 422

    def test_captura_com_texto_vazio_retorna_422(self, client, token_valido):
        resposta = client.post(
            "/api/vagas/capturar",
            json={"texto": ""},
            headers={"Authorization": f"Bearer {token_valido}"},
        )

        assert resposta.status_code == 422

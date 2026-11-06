from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_repositorio_token
from jobsync.token_captura.adapters import TokenCapturaRepositoryFake


@pytest.fixture
def repositorio() -> TokenCapturaRepositoryFake:
    return TokenCapturaRepositoryFake()


@pytest.fixture
def client(repositorio: TokenCapturaRepositoryFake) -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_repositorio_token] = lambda: repositorio

    yield TestClient(app)

    app.dependency_overrides.pop(obter_repositorio_token, None)


class TestTokenCapturaRouter:
    def test_post_token_captura_retorna_201_com_token(self, client: TestClient):
        response = client.post("/v1/tokens-captura", json={"perfil_identificador": "adriano"})

        assert response.status_code == 201
        corpo = response.json()
        assert corpo["perfil_identificador"] == "adriano"
        assert corpo["token"]

    def test_post_token_captura_persiste_token_resolvivel(
        self, client: TestClient, repositorio: TokenCapturaRepositoryFake
    ):
        response = client.post("/v1/tokens-captura", json={"perfil_identificador": "adriano"})

        assert repositorio.resolver_perfil_por_token(response.json()["token"]) == "adriano"

    def test_post_token_captura_sem_perfil_retorna_422(self, client: TestClient):
        response = client.post("/v1/tokens-captura", json={})

        assert response.status_code == 422
        assert response.json()["status"] == 422

    def test_post_token_captura_com_perfil_em_branco_retorna_422(self, client: TestClient):
        response = client.post("/v1/tokens-captura", json={"perfil_identificador": "   "})

        assert response.status_code == 422

    def test_post_token_captura_documentado_no_openapi(self, client: TestClient):
        response = client.get("/openapi.json")

        operacao = response.json()["paths"]["/v1/tokens-captura"]["post"]
        assert operacao["summary"] == "Gerar token de captura"
        assert "201" in operacao["responses"]

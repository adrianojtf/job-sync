import base64
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.curriculo_salvo.adapters.curriculo_salvo_repository_fake import (
    CurriculoSalvoRepositoryFake,
)
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import (
    obter_repositorio_curriculo_salvo,
    obter_repositorio_perfil_estruturado,
)
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)

PDF_BASE64 = base64.b64encode(b"%PDF-1.4 teste").decode()


def _perfil(**alteracoes) -> dict:
    return {
        "perfil_identificador": "adriano",
        "nome_completo": "Adriano Teixeira",
        "email": "adriano@email.com",
        "linkedin": "",
        "resumo_profissional": "",
        "experiencias": [],
        **alteracoes,
    }


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_repositorio_curriculo_salvo] = lambda: CurriculoSalvoRepositoryFake()
    app.dependency_overrides[obter_repositorio_perfil_estruturado] = lambda: PerfilEstruturadoRepositoryFake()

    yield TestClient(app)

    app.dependency_overrides.pop(obter_repositorio_curriculo_salvo, None)
    app.dependency_overrides.pop(obter_repositorio_perfil_estruturado, None)


class TestErrosDeDominioRouter:
    def test_salvar_curriculo_acima_do_limite_retorna_422_com_mensagem(self):
        repositorio = CurriculoSalvoRepositoryFake()
        app.dependency_overrides[obter_repositorio_curriculo_salvo] = lambda: repositorio
        client = TestClient(app)
        for indice in range(10):
            client.post(
                "/v1/curriculos",
                json={"perfil_identificador": "adriano", "nome_referencia": f"cv{indice}", "pdf_base64": PDF_BASE64},
            )

        response = client.post(
            "/v1/curriculos",
            json={"perfil_identificador": "adriano", "nome_referencia": "cv10", "pdf_base64": PDF_BASE64},
        )

        app.dependency_overrides.pop(obter_repositorio_curriculo_salvo, None)
        assert response.status_code == 422
        assert "Limite de 10" in response.json()["detail"]

    def test_salvar_perfil_com_experiencia_sem_empresa_retorna_422(self, client: TestClient):
        experiencia = {"empresa": " ", "cargo": "Dev", "periodo": "2020", "descricao": ""}

        response = client.post("/v1/perfil-estruturado", json=_perfil(experiencias=[experiencia]))

        assert response.status_code == 422
        assert "empresa" in response.json()["detail"]

    def test_atualizar_perfil_sem_email_retorna_422(self, client: TestClient):
        response = client.put("/v1/perfil-estruturado/adriano", json=_perfil(email=""))

        assert response.status_code == 422
        assert "email" in response.json()["detail"]

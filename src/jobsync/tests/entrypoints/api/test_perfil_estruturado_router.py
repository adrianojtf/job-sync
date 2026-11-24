from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_repositorio_perfil_estruturado
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)


@pytest.fixture
def repositorio() -> PerfilEstruturadoRepositoryFake:
    return PerfilEstruturadoRepositoryFake()


@pytest.fixture
def client(repositorio) -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_repositorio_perfil_estruturado] = lambda: repositorio

    yield TestClient(app)

    app.dependency_overrides.pop(obter_repositorio_perfil_estruturado, None)


def _corpo(**overrides) -> dict:
    corpo = {
        "perfil_identificador": "adriano",
        "nome_completo": "Adriano Teixeira",
        "email": "adriano@email.com",
        "linkedin": "",
        "resumo_profissional": "Backend.",
        "experiencias": [
            {
                "empresa": "Starian",
                "cargo": "Dev",
                "periodo": "2024 - Atual",
                "descricao": "",
                "contexto": "ERP para construção civil.",
                "responsabilidades": ["Projetar telas"],
                "conquistas": [{"texto": "Atendi 1.000 usuários."}],
                "skills": ["Java", "Flyway"],
            }
        ],
        "tecnologias": ["Java"],
    }
    corpo.update(overrides)
    return corpo


class TestPerfilEstruturadoRouter:
    def test_put_grava_os_quatro_blocos_e_devolve_as_tecnologias_incluidas(self, client: TestClient, repositorio):
        resposta = client.put("/v1/perfil-estruturado/adriano", json=_corpo())

        assert resposta.status_code == 200
        corpo = resposta.json()
        experiencia = corpo["experiencias"][0]
        assert experiencia["contexto"] == "ERP para construção civil."
        assert experiencia["responsabilidades"] == ["Projetar telas"]
        assert experiencia["skills"] == ["Java", "Flyway"]
        assert corpo["tecnologias"] == ["Java", "Flyway"]
        assert corpo["tecnologias_incluidas"] == ["Flyway"]
        assert repositorio.buscar_por_perfil("adriano").tecnologias == ("Java", "Flyway")

    def test_post_tambem_devolve_as_tecnologias_incluidas(self, client: TestClient):
        resposta = client.post("/v1/perfil-estruturado", json=_corpo())

        assert resposta.status_code == 200
        assert resposta.json()["tecnologias_incluidas"] == ["Flyway"]

    def test_contrato_anterior_sem_os_blocos_continua_aceito(self, client: TestClient):
        corpo = _corpo(
            experiencias=[{"empresa": "Starian", "cargo": "Dev", "periodo": "2024", "descricao": "Backend."}]
        )

        resposta = client.put("/v1/perfil-estruturado/adriano", json=corpo)

        assert resposta.status_code == 200
        experiencia = resposta.json()["experiencias"][0]
        assert (experiencia["contexto"], experiencia["responsabilidades"], experiencia["skills"]) == ("", [], [])
        assert resposta.json()["tecnologias_incluidas"] == []

    def test_skill_duplicada_na_experiencia_devolve_422(self, client: TestClient):
        corpo = _corpo()
        corpo["experiencias"][0]["skills"] = ["Java", "java"]

        resposta = client.put("/v1/perfil-estruturado/adriano", json=corpo)

        assert resposta.status_code == 422

    def test_get_devolve_os_blocos_gravados(self, client: TestClient):
        client.put("/v1/perfil-estruturado/adriano", json=_corpo())

        resposta = client.get("/v1/perfil-estruturado/adriano")

        assert resposta.json()["experiencias"][0]["skills"] == ["Java", "Flyway"]
        assert resposta.json()["tecnologias_incluidas"] == []

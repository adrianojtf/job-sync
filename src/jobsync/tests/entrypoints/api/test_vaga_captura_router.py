from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.dependencies import obter_repositorio_vaga
from jobsync.entrypoints.api.main import app
from jobsync.vaga.adapters import VagaRepositoryFake


@pytest.fixture
def repositorio() -> Generator[VagaRepositoryFake, None, None]:
    repo = VagaRepositoryFake()
    app.dependency_overrides[obter_repositorio_vaga] = lambda: repo
    yield repo
    app.dependency_overrides.pop(obter_repositorio_vaga, None)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestCapturaDeVagaComDadosExtraidos:
    def test_post_guarda_e_devolve_cargo_empresa_e_local(self, client: TestClient, repositorio):
        response = client.post(
            "/v1/vagas",
            json={
                "perfil_identificador": "matheus",
                "texto_descricao": "Descrição da vaga",
                "url_origem": "https://www.linkedin.com/jobs/view/4484559483/",
                "cargo": "Engenheiro de Software",
                "empresa": "Barte",
                "local": "Brasil",
            },
        )

        assert response.status_code == 201
        corpo = response.json()
        assert corpo["cargo"] == "Engenheiro de Software"
        assert corpo["empresa"] == "Barte"
        assert corpo["local"] == "Brasil"
        salva = repositorio.listar_nao_convertidas("matheus")[0]
        assert salva.cargo == "Engenheiro de Software"

    def test_post_sem_os_novos_campos_continua_valido_e_devolve_nulos(self, client: TestClient, repositorio):
        response = client.post(
            "/v1/vagas",
            json={"perfil_identificador": "matheus", "texto_descricao": "Descrição da vaga"},
        )

        assert response.status_code == 201
        corpo = response.json()
        assert corpo["cargo"] is None
        assert corpo["empresa"] is None
        assert corpo["local"] is None

    def test_get_lista_os_dados_extraidos(self, client: TestClient, repositorio):
        client.post(
            "/v1/vagas",
            json={
                "perfil_identificador": "matheus",
                "texto_descricao": "Descrição da vaga",
                "cargo": "Engenheiro",
                "empresa": "Barte",
            },
        )

        response = client.get("/v1/vagas?perfil_identificador=matheus")

        item = response.json()["items"][0]
        assert item["cargo"] == "Engenheiro"
        assert item["empresa"] == "Barte"
        assert item["local"] is None

    @pytest.mark.parametrize("campo", ["cargo", "empresa", "local"])
    def test_post_rejeita_campo_acima_do_limite(self, client: TestClient, repositorio, campo):
        response = client.post(
            "/v1/vagas",
            json={"perfil_identificador": "matheus", "texto_descricao": "Descrição", campo: "a" * 201},
        )

        assert response.status_code == 422
        assert repositorio.listar_nao_convertidas("matheus") == ()

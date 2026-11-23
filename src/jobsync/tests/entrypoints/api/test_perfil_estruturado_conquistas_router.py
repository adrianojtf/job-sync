from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_repositorio_perfil_estruturado
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)


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


def _experiencia(**alteracoes) -> dict:
    return {"empresa": "TechCorp", "cargo": "Dev", "periodo": "2020", "descricao": "Backend.", **alteracoes}


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    repositorio = PerfilEstruturadoRepositoryFake()
    app.dependency_overrides[obter_repositorio_perfil_estruturado] = lambda: repositorio

    yield TestClient(app)

    app.dependency_overrides.pop(obter_repositorio_perfil_estruturado, None)


class TestConquistasNoPerfilEstruturado:
    def test_salvar_e_buscar_perfil_devolve_as_conquistas_com_origem(self, client: TestClient):
        conquistas = [
            {"texto": "Reduzi o tempo de deploy.", "origem": "MANUAL"},
            {"texto": "Atuei com o cliente em um MVP.", "origem": "RESPOSTA_PERGUNTA"},
        ]

        salvar = client.put("/v1/perfil-estruturado/adriano", json=_perfil(experiencias=[_experiencia(conquistas=conquistas)]))
        buscar = client.get("/v1/perfil-estruturado/adriano")

        assert salvar.status_code == 200
        assert buscar.json()["experiencias"][0]["conquistas"] == conquistas

    def test_payload_antigo_sem_conquistas_continua_valido(self, client: TestClient):
        resposta = client.put("/v1/perfil-estruturado/adriano", json=_perfil(experiencias=[_experiencia()]))

        assert resposta.status_code == 200
        assert resposta.json()["experiencias"][0]["conquistas"] == []

    def test_origem_omitida_vira_manual(self, client: TestClient):
        experiencia = _experiencia(conquistas=[{"texto": "Reduzi o tempo de deploy."}])

        resposta = client.put("/v1/perfil-estruturado/adriano", json=_perfil(experiencias=[experiencia]))

        assert resposta.json()["experiencias"][0]["conquistas"][0]["origem"] == "MANUAL"

    def test_origem_invalida_retorna_422(self, client: TestClient):
        experiencia = _experiencia(conquistas=[{"texto": "Reduzi o tempo de deploy.", "origem": "OUTRA"}])

        resposta = client.put("/v1/perfil-estruturado/adriano", json=_perfil(experiencias=[experiencia]))

        assert resposta.status_code == 422

    def test_conquista_duplicada_na_experiencia_retorna_422(self, client: TestClient):
        conquistas = [{"texto": "Reduzi o tempo de deploy."}, {"texto": "reduzi o TEMPO de deploy"}]

        resposta = client.put("/v1/perfil-estruturado/adriano", json=_perfil(experiencias=[_experiencia(conquistas=conquistas)]))

        assert resposta.status_code == 422
        assert "duplicadas" in resposta.json()["detail"]

    def test_conquista_com_texto_vazio_retorna_422(self, client: TestClient):
        experiencia = _experiencia(conquistas=[{"texto": "  "}])

        resposta = client.put("/v1/perfil-estruturado/adriano", json=_perfil(experiencias=[experiencia]))

        assert resposta.status_code == 422


class TestConquistasParecidasRouter:
    def test_devolve_as_conquistas_parecidas(self, client: TestClient):
        parecida = "Reduzi o tempo de deploy em 40% com pipeline automatizado."

        resposta = client.post(
            "/v1/perfil-estruturado/conquistas/parecidas",
            json={
                "texto": "Reduzi o tempo de deploy com o pipeline automatizado",
                "conquistas": [parecida, "Liderei a migração do banco de dados."],
            },
        )

        assert resposta.status_code == 200
        assert resposta.json() == {"parecidas": [parecida]}

    def test_sem_parecidas_devolve_lista_vazia(self, client: TestClient):
        resposta = client.post(
            "/v1/perfil-estruturado/conquistas/parecidas",
            json={"texto": "Construí uma API.", "conquistas": ["Liderei a migração do banco de dados."]},
        )

        assert resposta.json() == {"parecidas": []}

    def test_texto_vazio_retorna_422(self, client: TestClient):
        resposta = client.post(
            "/v1/perfil-estruturado/conquistas/parecidas", json={"texto": " ", "conquistas": []}
        )

        assert resposta.status_code == 422

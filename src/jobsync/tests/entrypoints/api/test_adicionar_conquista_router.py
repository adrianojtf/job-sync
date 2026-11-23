from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_repositorio_perfil_estruturado
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)
from jobsync.perfil_estruturado.domain.perfil_estruturado import ExperienciaProfissional, PerfilEstruturado


@pytest.fixture
def repositorio() -> PerfilEstruturadoRepositoryFake:
    repositorio = PerfilEstruturadoRepositoryFake()
    repositorio.salvar(
        PerfilEstruturado(
            perfil_identificador="adriano",
            nome_completo="Adriano Teixeira",
            email="adriano@email.com",
            linkedin="",
            resumo_profissional="Backend.",
            experiencias=(
                ExperienciaProfissional("Neoway", "Dev Java", "2020", "APIs."),
                ExperienciaProfissional("TechCorp", "Engenheiro", "2022", "Backend."),
            ),
            formacoes=(),
            certificacoes=(),
            idiomas=(),
            tecnologias=("Java",),
        )
    )
    return repositorio


@pytest.fixture
def client(repositorio) -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_repositorio_perfil_estruturado] = lambda: repositorio

    yield TestClient(app)

    app.dependency_overrides.pop(obter_repositorio_perfil_estruturado, None)


URL = "/v1/perfil-estruturado/adriano/experiencias/1/conquistas"


class TestAdicionarConquistaRouter:
    def test_adiciona_a_conquista_e_devolve_o_perfil_atualizado(self, client: TestClient):
        resposta = client.post(URL, json={"texto": "Atuei com o cliente em um MVP."})

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["experiencias"][1]["conquistas"] == [
            {"texto": "Atuei com o cliente em um MVP.", "origem": "RESPOSTA_PERGUNTA"}
        ]
        assert corpo["experiencias"][0]["conquistas"] == []

    def test_a_conquista_fica_gravada_no_perfil(self, client: TestClient, repositorio):
        client.post(URL, json={"texto": "Atuei com o cliente em um MVP."})

        salvo = repositorio.buscar_por_perfil("adriano")
        assert [c.texto for c in salvo.experiencias[1].conquistas] == ["Atuei com o cliente em um MVP."]

    def test_perfil_inexistente_retorna_404(self, client: TestClient):
        resposta = client.post("/v1/perfil-estruturado/outro/experiencias/0/conquistas", json={"texto": "Algo."})

        assert resposta.status_code == 404

    def test_experiencia_inexistente_retorna_404(self, client: TestClient):
        resposta = client.post("/v1/perfil-estruturado/adriano/experiencias/7/conquistas", json={"texto": "Algo."})

        assert resposta.status_code == 404

    @pytest.mark.parametrize("texto", ["", "   "])
    def test_texto_vazio_retorna_422(self, client: TestClient, texto):
        resposta = client.post(URL, json={"texto": texto})

        assert resposta.status_code == 422

    def test_conquista_duplicada_retorna_422(self, client: TestClient):
        client.post(URL, json={"texto": "Atuei com o cliente em um MVP."})

        resposta = client.post(URL, json={"texto": "atuei com o CLIENTE em um MVP"})

        assert resposta.status_code == 422
        assert "duplicadas" in resposta.json()["detail"]

    def test_indice_negativo_retorna_422(self, client: TestClient):
        resposta = client.post("/v1/perfil-estruturado/adriano/experiencias/-1/conquistas", json={"texto": "Algo."})

        assert resposta.status_code == 422

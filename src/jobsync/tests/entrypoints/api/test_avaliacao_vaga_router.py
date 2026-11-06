from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.dependencies import obter_service_avaliar_descricao_vaga
from jobsync.entrypoints.api.main import app
from jobsync.shared_kernel.domain import ResultadoDimensaoAvaliacao
from jobsync.vaga.domain.avaliacao_descricao_vaga import AvaliacaoDescricaoVaga
from jobsync.vaga.service_layer.avaliar_descricao_vaga.exceptions import (
    AvaliacaoDescricaoVagaIndisponivel,
)


def _avaliacao() -> AvaliacaoDescricaoVaga:
    return AvaliacaoDescricaoVaga(
        completude=ResultadoDimensaoAvaliacao(75, "adequada", 0.82),
        clareza=ResultadoDimensaoAvaliacao(80, "clara", 0.87),
        relevancia=ResultadoDimensaoAvaliacao(85, "relevante", 0.91),
        inclusao=ResultadoDimensaoAvaliacao(70, "inclusiva", 0.76),
    )


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    yield TestClient(app)
    app.dependency_overrides.pop(obter_service_avaliar_descricao_vaga, None)


class TestAvaliacaoVagaRouter:
    def test_post_avaliacao_descricao_vaga(self, client: TestClient):
        class ServiceFake:
            def executar(self, input_dto):
                assert input_dto.descricao_vaga == "Descrição da vaga."
                return _avaliacao()

        app.dependency_overrides[obter_service_avaliar_descricao_vaga] = ServiceFake

        response = client.post(
            "/v1/vagas/avaliacoes",
            json={"descricao_vaga": "Descrição da vaga."},
        )

        assert response.status_code == 200
        dados = response.json()
        assert dados["score"] == 78
        assert dados["completude"] == {
            "score": 75,
            "nivel": "adequada",
            "confianca": 0.82,
        }
        assert dados["inclusao"]["score"] == 70

    @pytest.mark.parametrize("descricao", ["", "   "])
    def test_post_avaliacao_rejeita_texto_vazio(
        self, client: TestClient, descricao: str
    ):
        app.dependency_overrides[obter_service_avaliar_descricao_vaga] = lambda: None

        response = client.post(
            "/v1/vagas/avaliacoes",
            json={"descricao_vaga": descricao},
        )

        assert response.status_code == 422
        assert response.json()["status"] == 422
        assert response.json()["title"] == "Requisição inválida"

    def test_post_avaliacao_retorna_problem_details_quando_jev_indisponivel(
        self, client: TestClient
    ):
        class ServiceFake:
            def executar(self, input_dto):
                raise AvaliacaoDescricaoVagaIndisponivel()

        app.dependency_overrides[obter_service_avaliar_descricao_vaga] = ServiceFake

        response = client.post(
            "/v1/vagas/avaliacoes",
            json={"descricao_vaga": "Descrição da vaga."},
        )

        assert response.status_code == 502
        assert response.json()["title"] == "Avaliação de vaga indisponível"
        assert response.json()["detail"] == (
            "O serviço de avaliação de vagas está indisponível."
        )

    def test_openapi_documenta_sucesso_e_erros(self, client: TestClient):
        openapi = client.get("/openapi.json").json()
        operacao = openapi["paths"]["/v1/vagas/avaliacoes"]["post"]

        assert "200" in operacao["responses"]
        assert "422" in operacao["responses"]
        assert "502" in operacao["responses"]

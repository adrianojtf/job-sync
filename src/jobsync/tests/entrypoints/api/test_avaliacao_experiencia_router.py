from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.curriculo import AvaliacaoExperiencia
from jobsync.curriculo.service_layer.avaliar_experiencia.exceptions import (
    AvaliacaoExperienciaIndisponivel,
)
from jobsync.entrypoints.api.dependencies import obter_service_avaliar_experiencia
from jobsync.entrypoints.api.main import app
from jobsync.shared_kernel.domain import ResultadoDimensaoAvaliacao


def _avaliacao() -> AvaliacaoExperiencia:
    return AvaliacaoExperiencia(
        clareza_escrita=ResultadoDimensaoAvaliacao(80, "clara", 0.84),
        qualidade_detalhe=ResultadoDimensaoAvaliacao(75, "detalhada", 0.79),
        aderencia_vaga=ResultadoDimensaoAvaliacao(70, "boa aderencia", 0.81),
        consistencia_textual=ResultadoDimensaoAvaliacao(70, "consistente", 0.73),
    )


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    yield TestClient(app)
    app.dependency_overrides.pop(obter_service_avaliar_experiencia, None)


class TestAvaliacaoExperienciaRouter:
    def test_post_avaliacao_experiencia(self, client: TestClient):
        class ServiceFake:
            def executar(self, input_dto):
                assert input_dto.experiencia.descricao == "Desenvolvi serviços Python."
                assert input_dto.descricao_vaga == "Vaga backend Python."
                return _avaliacao()

        app.dependency_overrides[obter_service_avaliar_experiencia] = ServiceFake

        response = client.post(
            "/v1/experiencias-profissionais/avaliacoes",
            json={
                "experiencia": {
                    "cargo": "Pessoa desenvolvedora backend",
                    "empresa": "TechCorp",
                    "periodo": "2022-2025",
                    "descricao": "Desenvolvi serviços Python.",
                },
                "descricao_vaga": "Vaga backend Python.",
            },
        )

        assert response.status_code == 200
        dados = response.json()
        assert dados["score"] == 74
        assert dados["clareza_escrita"]["score"] == 80
        assert dados["consistencia_textual"]["nivel"] == "consistente"

    @pytest.mark.parametrize(
        "body",
        [
            {
                "experiencia": {"descricao": "   "},
                "descricao_vaga": "Vaga backend.",
            },
            {
                "experiencia": {"descricao": "Texto válido."},
                "descricao_vaga": "   ",
            },
        ],
    )
    def test_post_avaliacao_rejeita_texto_vazio(
        self, client: TestClient, body: dict
    ):
        app.dependency_overrides[obter_service_avaliar_experiencia] = lambda: None

        response = client.post(
            "/v1/experiencias-profissionais/avaliacoes",
            json=body,
        )

        assert response.status_code == 422
        assert response.json()["status"] == 422
        assert response.json()["title"] == "Requisição inválida"

    def test_post_avaliacao_retorna_problem_details_quando_jev_indisponivel(
        self, client: TestClient
    ):
        class ServiceFake:
            def executar(self, input_dto):
                raise AvaliacaoExperienciaIndisponivel()

        app.dependency_overrides[obter_service_avaliar_experiencia] = ServiceFake

        response = client.post(
            "/v1/experiencias-profissionais/avaliacoes",
            json={
                "experiencia": {"descricao": "Experiência."},
                "descricao_vaga": "Vaga backend.",
            },
        )

        assert response.status_code == 502
        assert response.json()["title"] == "Avaliação de experiência indisponível"
        assert response.json()["detail"] == (
            "O serviço de avaliação de experiência está indisponível."
        )

    def test_openapi_documenta_sucesso_e_erros(self, client: TestClient):
        openapi = client.get("/openapi.json").json()
        operacao = openapi["paths"]["/v1/experiencias-profissionais/avaliacoes"]["post"]

        assert "200" in operacao["responses"]
        assert "422" in operacao["responses"]
        assert "502" in operacao["responses"]

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.curriculo.domain.lacuna_da_vaga import LacunaDaVaga
from jobsync.curriculo.domain.redator_conquista_port import RedatorConquistaPort
from jobsync.curriculo.service_layer.redigir_conquista_de_lacuna import RedigirConquistaDeLacuna
from jobsync.entrypoints.api.dependencies import obter_service_redigir_conquista_de_lacuna
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_repositorio_perfil_estruturado
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)
from jobsync.perfil_estruturado.domain.perfil_estruturado import ExperienciaProfissional, PerfilEstruturado


class RedatorFake(RedatorConquistaPort):
    def __init__(self, erro: Exception | None = None):
        self._erro = erro
        self.chamadas: list[tuple[LacunaDaVaga, str, str, str]] = []

    def redigir(self, lacuna, caso, cargo, idioma_alvo):
        self.chamadas.append((lacuna, caso, cargo, idioma_alvo))
        if self._erro is not None:
            raise self._erro
        return "Construí um MVP do zero."


CORPO = {
    "perfil_identificador": "adriano",
    "tema": "Construção de MVPs",
    "pergunta": "Você já construiu um MVP do zero?",
    "caso": "Montei o MVP de pagamentos em 6 semanas.",
    "experiencia_indice": 1,
    "idioma_alvo": "pt",
}


@pytest.fixture
def redator() -> RedatorFake:
    return RedatorFake()


@pytest.fixture
def client(redator) -> Generator[TestClient, None, None]:
    repositorio = PerfilEstruturadoRepositoryFake()
    repositorio.salvar(
        PerfilEstruturado(
            perfil_identificador="adriano",
            nome_completo="Adriano Teixeira",
            email="adriano@email.com",
            linkedin="",
            resumo_profissional="",
            experiencias=(
                ExperienciaProfissional("Neoway", "Dev Java", "2020", "APIs."),
                ExperienciaProfissional("TechCorp", "Engenheiro de Software", "2022", "Backend."),
            ),
            formacoes=(),
            certificacoes=(),
            idiomas=(),
            tecnologias=(),
        )
    )
    app.dependency_overrides[obter_repositorio_perfil_estruturado] = lambda: repositorio
    app.dependency_overrides[obter_service_redigir_conquista_de_lacuna] = lambda: RedigirConquistaDeLacuna(redator)

    yield TestClient(app)

    app.dependency_overrides.pop(obter_repositorio_perfil_estruturado, None)
    app.dependency_overrides.pop(obter_service_redigir_conquista_de_lacuna, None)


class TestConquistaRascunhoRouter:
    def test_devolve_o_texto_redigido_sem_persistir(self, client: TestClient):
        resposta = client.post("/v1/curriculos/lacunas/conquista-rascunho", json=CORPO)

        assert resposta.status_code == 200
        assert resposta.json() == {"texto": "Construí um MVP do zero."}

    def test_usa_o_cargo_da_experiencia_escolhida(self, client: TestClient, redator: RedatorFake):
        client.post("/v1/curriculos/lacunas/conquista-rascunho", json=CORPO)

        lacuna, caso, cargo, idioma = redator.chamadas[0]
        assert lacuna == LacunaDaVaga("Construção de MVPs", "Você já construiu um MVP do zero?")
        assert caso == "Montei o MVP de pagamentos em 6 semanas."
        assert cargo == "Engenheiro de Software"
        assert idioma == "pt"

    @pytest.mark.parametrize("indice", [2, 9])
    def test_experiencia_inexistente_retorna_404(self, client: TestClient, indice):
        resposta = client.post(
            "/v1/curriculos/lacunas/conquista-rascunho", json={**CORPO, "experiencia_indice": indice}
        )

        assert resposta.status_code == 404

    def test_indice_negativo_retorna_422(self, client: TestClient):
        resposta = client.post(
            "/v1/curriculos/lacunas/conquista-rascunho", json={**CORPO, "experiencia_indice": -1}
        )

        assert resposta.status_code == 422

    def test_caso_vazio_retorna_422(self, client: TestClient):
        resposta = client.post("/v1/curriculos/lacunas/conquista-rascunho", json={**CORPO, "caso": "  "})

        assert resposta.status_code == 422

    def test_perfil_inexistente_retorna_422(self, client: TestClient):
        resposta = client.post(
            "/v1/curriculos/lacunas/conquista-rascunho", json={**CORPO, "perfil_identificador": "outro"}
        )

        assert resposta.status_code == 422

    def test_ia_indisponivel_retorna_502(self, client: TestClient, redator: RedatorFake):
        app.dependency_overrides[obter_service_redigir_conquista_de_lacuna] = lambda: RedigirConquistaDeLacuna(
            RedatorFake(erro=RuntimeError("falha"))
        )

        resposta = client.post("/v1/curriculos/lacunas/conquista-rascunho", json=CORPO)

        assert resposta.status_code == 502

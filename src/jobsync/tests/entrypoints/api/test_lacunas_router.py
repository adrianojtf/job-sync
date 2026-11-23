from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.curriculo.domain.identificador_lacunas_port import IdentificadorLacunasPort
from jobsync.curriculo.domain.lacuna_da_vaga import LacunaDaVaga
from jobsync.curriculo.service_layer.identificar_lacunas_da_vaga import IdentificarLacunasDaVaga
from jobsync.entrypoints.api.dependencies import obter_service_identificar_lacunas_da_vaga
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_repositorio_perfil_estruturado
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)
from jobsync.perfil_estruturado.domain.perfil_estruturado import (
    Conquista,
    ExperienciaProfissional,
    PerfilEstruturado,
)

LACUNAS = (
    LacunaDaVaga("Atuação junto ao cliente", "Você já atuou junto ao cliente?"),
    LacunaDaVaga("Construção de MVPs", "Você já construiu um MVP do zero?"),
)


class IdentificadorFake(IdentificadorLacunasPort):
    def __init__(self, lacunas=LACUNAS, erro: Exception | None = None):
        self._lacunas = lacunas
        self._erro = erro
        self.chamadas = []

    def identificar(self, historico, contexto):
        self.chamadas.append((historico, contexto))
        if self._erro is not None:
            raise self._erro
        return self._lacunas


def _perfil(experiencias: tuple[ExperienciaProfissional, ...]) -> PerfilEstruturado:
    return PerfilEstruturado(
        perfil_identificador="adriano",
        nome_completo="Adriano Teixeira",
        email="adriano@email.com",
        linkedin="",
        resumo_profissional="Engenheiro backend.",
        experiencias=experiencias,
        formacoes=(),
        certificacoes=(),
        idiomas=(),
        tecnologias=("Java", "PostgreSQL"),
    )


EXPERIENCIA = ExperienciaProfissional(
    empresa="TechCorp",
    cargo="Dev",
    periodo="2020",
    descricao="Backend em Java.",
    conquistas=(Conquista("Reduzi o tempo de deploy."),),
)

CORPO = {
    "perfil_identificador": "adriano",
    "descricao_vaga": "Atuar junto ao cliente e construir MVPs.",
    "cargo_alvo": "Forward Deployed Engineer",
    "idioma_alvo": "pt",
}


@pytest.fixture
def identificador() -> IdentificadorFake:
    return IdentificadorFake()


@pytest.fixture
def repositorio() -> PerfilEstruturadoRepositoryFake:
    repositorio = PerfilEstruturadoRepositoryFake()
    repositorio.salvar(_perfil((EXPERIENCIA,)))
    return repositorio


@pytest.fixture
def client(identificador, repositorio) -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_repositorio_perfil_estruturado] = lambda: repositorio
    app.dependency_overrides[obter_service_identificar_lacunas_da_vaga] = lambda: IdentificarLacunasDaVaga(
        identificador
    )

    yield TestClient(app)

    app.dependency_overrides.pop(obter_repositorio_perfil_estruturado, None)
    app.dependency_overrides.pop(obter_service_identificar_lacunas_da_vaga, None)


class TestLacunasRouter:
    def test_devolve_as_lacunas_com_tema_e_pergunta(self, client: TestClient):
        resposta = client.post("/v1/curriculos/lacunas", json=CORPO)

        assert resposta.status_code == 200
        assert resposta.json() == {
            "lacunas": [
                {"tema": "Atuação junto ao cliente", "pergunta": "Você já atuou junto ao cliente?"},
                {"tema": "Construção de MVPs", "pergunta": "Você já construiu um MVP do zero?"},
            ]
        }

    def test_monta_o_historico_do_perfil_com_as_conquistas_e_o_contexto_da_vaga(
        self, client: TestClient, identificador: IdentificadorFake
    ):
        client.post("/v1/curriculos/lacunas", json=CORPO)

        historico, contexto = identificador.chamadas[0]
        assert historico.resumo == "Engenheiro backend."
        assert historico.tecnologias == ("Java", "PostgreSQL")
        assert historico.experiencias[0].conquistas == ("Reduzi o tempo de deploy.",)
        assert contexto.descricao_vaga == CORPO["descricao_vaga"]
        assert contexto.cargo_alvo == "Forward Deployed Engineer"
        assert contexto.idioma_alvo == "pt"

    def test_perfil_sem_experiencias_devolve_lista_vazia_sem_chamar_a_ia(
        self, client: TestClient, identificador: IdentificadorFake, repositorio: PerfilEstruturadoRepositoryFake
    ):
        repositorio.salvar(_perfil(()))

        resposta = client.post("/v1/curriculos/lacunas", json=CORPO)

        assert resposta.json() == {"lacunas": []}
        assert identificador.chamadas == []

    def test_falha_da_ia_devolve_lista_vazia(self, repositorio: PerfilEstruturadoRepositoryFake):
        app.dependency_overrides[obter_repositorio_perfil_estruturado] = lambda: repositorio
        app.dependency_overrides[obter_service_identificar_lacunas_da_vaga] = lambda: IdentificarLacunasDaVaga(
            IdentificadorFake(erro=RuntimeError("falha"))
        )

        resposta = TestClient(app).post("/v1/curriculos/lacunas", json=CORPO)

        app.dependency_overrides.pop(obter_repositorio_perfil_estruturado, None)
        app.dependency_overrides.pop(obter_service_identificar_lacunas_da_vaga, None)
        assert resposta.status_code == 200
        assert resposta.json() == {"lacunas": []}

    def test_perfil_inexistente_retorna_422(self, client: TestClient):
        resposta = client.post("/v1/curriculos/lacunas", json={**CORPO, "perfil_identificador": "outro"})

        assert resposta.status_code == 422
        assert "Perfil estruturado" in resposta.json()["detail"]

    @pytest.mark.parametrize("alteracao", [{"descricao_vaga": "  "}, {"idioma_alvo": "fr"}])
    def test_vaga_vazia_ou_idioma_invalido_retorna_422(self, client: TestClient, alteracao):
        resposta = client.post("/v1/curriculos/lacunas", json={**CORPO, **alteracao})

        assert resposta.status_code == 422

    def test_sem_perfil_identificador_retorna_422(self, client: TestClient):
        corpo = {chave: valor for chave, valor in CORPO.items() if chave != "perfil_identificador"}

        resposta = client.post("/v1/curriculos/lacunas", json=corpo)

        assert resposta.status_code == 422

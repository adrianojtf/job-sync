"""Contrato HTTP de /curriculos-adaptados: salvar, listar, abrir e editar o currículo adaptado."""
import base64
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.curriculo_adaptado.adapters import CurriculoAdaptadoRepositoryFake
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.api.schemas.curriculo import RascunhoCurriculoAdaptadoSchema
from jobsync.entrypoints.api.schemas.vaga import AnaliseVagaSchema
from jobsync.entrypoints.dependencies import obter_repositorio_curriculo_adaptado
from jobsync.tests.curriculo_adaptado.exemplos import analise_vaga, rascunho


@pytest.fixture
def repositorio() -> CurriculoAdaptadoRepositoryFake:
    return CurriculoAdaptadoRepositoryFake()


@pytest.fixture
def client(repositorio) -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_repositorio_curriculo_adaptado] = lambda: repositorio
    yield TestClient(app)
    app.dependency_overrides.pop(obter_repositorio_curriculo_adaptado, None)


def _corpo_de_salvar(perfil: str = "ana", **sobrescritas) -> dict:
    corpo = {
        "perfil_identificador": perfil,
        "rascunho": RascunhoCurriculoAdaptadoSchema.from_domain(rascunho()).model_dump(),
        "idioma_alvo": "pt",
        "cargo_alvo": "Engenheira de Software",
        "empresa_alvo": "TechCorp",
        "descricao_vaga": "Vaga Java com code review.",
        "analise_vaga": AnaliseVagaSchema.from_domain(analise_vaga()).model_dump(),
    }
    corpo.update(sobrescritas)
    return corpo


def _salvar(client: TestClient, perfil: str = "ana", **sobrescritas) -> dict:
    resposta = client.post("/v1/curriculos-adaptados", json=_corpo_de_salvar(perfil, **sobrescritas))
    assert resposta.status_code == 201
    return resposta.json()


class TestSalvar:
    def test_salva_e_devolve_o_id_e_o_pdf(self, client, repositorio):
        resposta = client.post("/v1/curriculos-adaptados", json=_corpo_de_salvar())

        assert resposta.status_code == 201
        corpo = resposta.json()
        assert corpo["id"]
        assert corpo["nome_arquivo"].endswith("-EngenheiraDeSoftware-Techcorp.pdf")
        assert base64.b64decode(corpo["pdf_base64"]).startswith(b"%PDF")
        assert repositorio.buscar(corpo["id"], "ana") is not None

    def test_o_header_location_aponta_para_o_recurso(self, client):
        resposta = client.post("/v1/curriculos-adaptados", json=_corpo_de_salvar())

        assert resposta.headers["Location"].endswith(f"/v1/curriculos-adaptados/{resposta.json()['id']}")

    @pytest.mark.parametrize(
        "campo, valor",
        [("idioma_alvo", "fr"), ("cargo_alvo", " "), ("empresa_alvo", " "), ("descricao_vaga", " ")],
    )
    def test_dados_invalidos_devolvem_422(self, client, campo, valor):
        resposta = client.post("/v1/curriculos-adaptados", json=_corpo_de_salvar(**{campo: valor}))

        assert resposta.status_code == 422

    def test_competencias_junto_com_a_secao_de_tecnologias_devolve_422(self, client):
        corpo = _corpo_de_salvar()
        corpo["rascunho"]["secoes"].append(
            {"tipo": "TECNOLOGIAS", "titulo": "Tecnologias", "conteudo": "Java"}
        )

        assert client.post("/v1/curriculos-adaptados", json=corpo).status_code == 422


class TestListarEBuscar:
    def test_lista_so_os_do_perfil_com_o_resumo(self, client):
        meu = _salvar(client, "ana")
        _salvar(client, "bia")

        resposta = client.get("/v1/curriculos-adaptados", params={"perfil_identificador": "ana"})

        assert resposta.status_code == 200
        assert resposta.json()["total"] == 1
        item = resposta.json()["items"][0]
        assert item["id"] == meu["id"]
        assert item["cargo_alvo"] == "Engenheira de Software"
        assert item["empresa_alvo"] == "TechCorp"
        assert "rascunho" not in item
        assert "pdf_base64" not in item

    def test_abre_o_curriculo_completo_com_o_contexto_da_vaga(self, client):
        salvo = _salvar(client)

        resposta = client.get(
            f"/v1/curriculos-adaptados/{salvo['id']}", params={"perfil_identificador": "ana"}
        )

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["descricao_vaga"] == "Vaga Java com code review."
        assert corpo["analise_vaga"]["texto_original"] == "Vaga Java com code review."
        assert corpo["idioma_alvo"] == "pt"
        assert corpo["rascunho"]["competencias"] == [
            {"nome": "Linguagens", "tags": ["Java", "Python"]},
            {"nome": "Bancos de Dados", "tags": ["SQL"]},
        ]
        assert corpo["rascunho"]["titulo_competencias"] == "Competências"

    def test_id_inexistente_devolve_404(self, client):
        resposta = client.get(
            "/v1/curriculos-adaptados/nao-existe", params={"perfil_identificador": "ana"}
        )

        assert resposta.status_code == 404

    def test_curriculo_de_outro_perfil_devolve_404(self, client):
        salvo = _salvar(client, "bia")

        resposta = client.get(
            f"/v1/curriculos-adaptados/{salvo['id']}", params={"perfil_identificador": "ana"}
        )

        assert resposta.status_code == 404


class TestAtualizar:
    def _corpo_de_atualizar(self, perfil: str = "ana", tags=("Go",)) -> dict:
        editado = RascunhoCurriculoAdaptadoSchema.from_domain(rascunho()).model_dump()
        editado["competencias"] = [{"nome": "Linguagens", "tags": list(tags)}]
        return {"perfil_identificador": perfil, "rascunho": editado}

    def test_substitui_o_conteudo_e_devolve_o_pdf_novo(self, client, repositorio):
        salvo = _salvar(client)

        resposta = client.put(
            f"/v1/curriculos-adaptados/{salvo['id']}", json=self._corpo_de_atualizar()
        )

        assert resposta.status_code == 200
        assert base64.b64decode(resposta.json()["pdf_base64"]).startswith(b"%PDF")
        assert repositorio.buscar(salvo["id"], "ana").rascunho.competencias[0].tags == ("Go",)

    def test_a_edicao_aparece_ao_abrir_de_novo(self, client):
        salvo = _salvar(client)
        client.put(f"/v1/curriculos-adaptados/{salvo['id']}", json=self._corpo_de_atualizar())

        aberto = client.get(
            f"/v1/curriculos-adaptados/{salvo['id']}", params={"perfil_identificador": "ana"}
        ).json()

        assert aberto["rascunho"]["competencias"] == [{"nome": "Linguagens", "tags": ["Go"]}]

    def test_id_inexistente_devolve_404(self, client):
        resposta = client.put("/v1/curriculos-adaptados/nao-existe", json=self._corpo_de_atualizar())

        assert resposta.status_code == 404

    def test_curriculo_de_outro_perfil_devolve_404_e_nao_altera(self, client, repositorio):
        salvo = _salvar(client, "bia")

        resposta = client.put(
            f"/v1/curriculos-adaptados/{salvo['id']}", json=self._corpo_de_atualizar("ana")
        )

        assert resposta.status_code == 404
        assert repositorio.buscar(salvo["id"], "bia").rascunho.competencias[0].tags == ("Java", "Python")

    def test_rascunho_invalido_devolve_422(self, client):
        salvo = _salvar(client)
        corpo = self._corpo_de_atualizar()
        corpo["rascunho"]["nome_completo"] = " "

        resposta = client.put(f"/v1/curriculos-adaptados/{salvo['id']}", json=corpo)

        assert resposta.status_code == 422

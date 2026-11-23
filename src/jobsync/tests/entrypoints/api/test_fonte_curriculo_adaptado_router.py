"""Contrato HTTP: um currículo adaptado salvo como fonte (base) de outra adaptação."""
from collections.abc import Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from jobsync.curriculo import (
    AjustadorExperienciaPort,
    AjustadorTextoPort,
    ExperienciaAdaptada,
    ExtratorCurriculoPort,
    IdentificadorEquivalenciasPort,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import AdaptarCurriculoParaVaga
from jobsync.curriculo_adaptado.adapters import CurriculoAdaptadoRepositoryFake
from jobsync.entrypoints.api.dependencies import obter_service_adaptar_curriculo
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_repositorio_curriculo_adaptado
from jobsync.tests.curriculo_adaptado.exemplos import curriculo_adaptado
from jobsync.vaga import AnaliseVaga
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort

URL = "/v1/curriculos/adaptado/rascunhos-adaptados"


class Espioes:
    def __init__(self) -> None:
        self.secoes_ajustadas: list = []
        self.experiencias_recebidas: list = []


def _servico(espioes: Espioes) -> AdaptarCurriculoParaVaga:
    analisador = Mock(spec=JobDescriptionAnalyzerPort)
    analisador.analisar.return_value = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga")
    ajustador_texto = Mock(spec=AjustadorTextoPort)

    def ajustar_secao(secao, **_):
        espioes.secoes_ajustadas.append(secao)
        return secao

    ajustador_texto.ajustar_secao.side_effect = ajustar_secao
    ajustador_experiencia = Mock(spec=AjustadorExperienciaPort)

    def ajustar(experiencia, **_):
        espioes.experiencias_recebidas.append(experiencia)
        return ExperienciaAdaptada(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            conquistas=("Conquista nova.",),
            contexto="Contexto novo.",
        )

    ajustador_experiencia.ajustar.side_effect = ajustar
    identificador = Mock(spec=IdentificadorEquivalenciasPort)
    identificador.identificar.return_value = ()
    return AdaptarCurriculoParaVaga(
        extrator=Mock(spec=ExtratorCurriculoPort),
        analisador_vaga=analisador,
        ajustador_texto=ajustador_texto,
        ajustador_experiencia=ajustador_experiencia,
        identificador_equivalencias=identificador,
    )


@pytest.fixture
def espioes() -> Espioes:
    return Espioes()


@pytest.fixture
def repositorio() -> CurriculoAdaptadoRepositoryFake:
    repositorio = CurriculoAdaptadoRepositoryFake()
    repositorio.salvar(curriculo_adaptado())
    return repositorio


@pytest.fixture
def client(repositorio, espioes) -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_repositorio_curriculo_adaptado] = lambda: repositorio
    app.dependency_overrides[obter_service_adaptar_curriculo] = lambda: _servico(espioes)
    yield TestClient(app)
    app.dependency_overrides.pop(obter_repositorio_curriculo_adaptado, None)
    app.dependency_overrides.pop(obter_service_adaptar_curriculo, None)


def _corpo(**sobrescritas) -> dict:
    corpo = {
        "descricao_vaga": "Vaga Angular.",
        "idioma_alvo": "en",
        "cargo_alvo": "Senior Engineer",
        "empresa_alvo": "Globex",
        "perfil_identificador": "ana",
        "curriculo_adaptado_id": "adaptado-1",
    }
    corpo.update(sobrescritas)
    return corpo


class TestRascunhoAPartirDeUmCurriculoAdaptado:
    def test_adapta_a_partir_do_conteudo_salvo_e_devolve_um_rascunho_novo(self, client, espioes):
        resposta = client.post(URL, json=_corpo())

        assert resposta.status_code == 200
        rascunho = resposta.json()["rascunho"]
        assert rascunho["competencias"] == [
            {"nome": "Linguagens", "tags": ["Java", "Python"]},
            {"nome": "Bancos de Dados", "tags": ["SQL"]},
        ]
        assert rascunho["experiencias"][0]["conquistas"] == ["Conquista nova."]
        assert {secao.tipo.name for secao in espioes.secoes_ajustadas} >= {"PERFIL", "TECNOLOGIAS"}

    def test_as_experiencias_estruturadas_do_salvo_seguem_para_a_ia_de_experiencias(
        self, client, espioes
    ):
        client.post(URL, json=_corpo())

        (recebida,) = espioes.experiencias_recebidas
        assert (recebida.cargo, recebida.empresa) == ("Dev", "TechCorp")
        assert recebida.descricao == "- Criei APIs.\n- Reduzi custos em 30%.\nPlataforma de pagamentos."

    def test_o_curriculo_de_origem_nao_e_alterado(self, client, repositorio):
        antes = repositorio.buscar("adaptado-1", "ana")

        client.post(URL, json=_corpo())

        assert repositorio.buscar("adaptado-1", "ana") == antes
        assert len(repositorio.listar_por_perfil("ana")) == 1

    def test_nao_exige_o_perfil_estruturado(self, client):
        resposta = client.post(URL, json=_corpo())

        assert resposta.status_code == 200

    def test_curriculo_de_outro_perfil_devolve_404(self, client):
        resposta = client.post(URL, json=_corpo(perfil_identificador="bia"))

        assert resposta.status_code == 404

    def test_id_inexistente_devolve_404(self, client):
        resposta = client.post(URL, json=_corpo(curriculo_adaptado_id="nao-existe"))

        assert resposta.status_code == 404

    def test_duas_fontes_ao_mesmo_tempo_devolvem_422(self, client):
        resposta = client.post(URL, json=_corpo(pdf_base64="JVBERi0xLjQ="))

        assert resposta.status_code == 422

    def test_curriculo_adaptado_sem_perfil_devolve_422(self, client):
        corpo = _corpo()
        del corpo["perfil_identificador"]

        resposta = client.post(URL, json=corpo)

        assert resposta.status_code == 422

    def test_a_fonte_por_perfil_estruturado_continua_funcionando(self, client):
        corpo = _corpo()
        del corpo["curriculo_adaptado_id"]

        resposta = client.post(URL, json=corpo)

        assert resposta.status_code == 422
        assert "Perfil estruturado não encontrado" in resposta.json()["detail"]

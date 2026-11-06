import base64
from collections.abc import Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from jobsync.ats_score import ResultadoAtsScore
from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.entrypoints.api.dependencies import obter_service_candidatar_na_vaga_externa
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_repositorio_perfil_estruturado
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)
from jobsync.perfil_estruturado.domain.perfil_estruturado import (
    ExperienciaProfissional,
    PerfilEstruturado,
)
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.vaga_externa.service_layer.candidatar_na_vaga_externa import (
    CandidatarNaVagaExterna,
)

URL = "/v1/vagas/descobertas/candidaturas"
PDF_BYTES = b"%PDF-1.4 original"


def _curriculo() -> Curriculo:
    return Curriculo(
        nome_completo="Adriano Teixeira",
        email="adriano@email.com",
        linkedin="",
        secoes=(SecaoCurriculo(tipo=TipoSecao.TECNOLOGIAS, titulo="Tecnologias", conteudo="Java"),),
    )


def _perfil() -> PerfilEstruturado:
    return PerfilEstruturado(
        perfil_identificador="adriano",
        nome_completo="Adriano Teixeira",
        email="adriano@email.com",
        linkedin="",
        resumo_profissional="Engenheiro backend.",
        experiencias=(
            ExperienciaProfissional(
                empresa="Neoway",
                cargo="Desenvolvedor Java",
                periodo="2020-2024",
                descricao="APIs em Java e AWS.",
            ),
        ),
        formacoes=(),
        certificacoes=(),
        idiomas=(),
        tecnologias=("Java",),
    )


def _payload(**extras) -> dict:
    return {
        "vaga": {
            "titulo": "Backend Engineer",
            "empresa": "Olist",
            "descricao": "Vaga para Java e Kafka.",
            "url": "https://example.com/vaga/1",
            "fonte": "REMOTEOK",
        },
        "idioma_alvo": "pt",
        **extras,
    }


@pytest.fixture
def portas() -> dict[str, Mock]:
    requisito = RequisitoTecnico(
        nome="Kafka",
        categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
        tipo=TipoRequisitoTecnico.EXPLICITO,
        origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
    )
    extrator = Mock()
    extrator.extrair.return_value = _curriculo()
    analisador = Mock()
    analisador.analisar.return_value = AnaliseVaga(requisitos=(requisito,), ambiguidade=(), texto_original="vaga")
    ajustador = Mock()
    ajustador.ajustar_secao.side_effect = lambda secao, **_: secao
    gerador_pdf = Mock()
    gerador_pdf.gerar.return_value = b"%PDF-1.4 adaptado"
    calcular_ats = Mock()
    calcular_ats.executar.return_value = ResultadoAtsScore(nota=72, requisitos_faltantes=(requisito,))
    gerador_carta = Mock()
    gerador_carta.gerar.return_value = "Prezados, ..."
    return {
        "extrator": extrator,
        "analisador_vaga": analisador,
        "ajustador_texto": ajustador,
        "gerador_pdf": gerador_pdf,
        "calcular_ats_score": calcular_ats,
        "gerador_carta": gerador_carta,
    }


@pytest.fixture
def repositorio_perfil() -> PerfilEstruturadoRepositoryFake:
    return PerfilEstruturadoRepositoryFake()


@pytest.fixture
def client(
    portas: dict[str, Mock], repositorio_perfil: PerfilEstruturadoRepositoryFake
) -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_service_candidatar_na_vaga_externa] = lambda: CandidatarNaVagaExterna(**portas)
    app.dependency_overrides[obter_repositorio_perfil_estruturado] = lambda: repositorio_perfil

    yield TestClient(app)

    app.dependency_overrides.pop(obter_service_candidatar_na_vaga_externa, None)
    app.dependency_overrides.pop(obter_repositorio_perfil_estruturado, None)


class TestCandidatarVagaExternaRouter:
    def test_com_pdf_retorna_artefatos_da_candidatura(self, client: TestClient, portas: dict[str, Mock]):
        response = client.post(URL, json=_payload(pdf_base64=base64.b64encode(PDF_BYTES).decode()))

        assert response.status_code == 200
        corpo = response.json()
        assert base64.b64decode(corpo["pdf_base64"]) == b"%PDF-1.4 adaptado"
        assert corpo["nome_arquivo"].endswith(".pdf")
        assert corpo["nota"] == 72
        assert corpo["requisitos_faltantes"] == [{"nome": "Kafka", "categoria": "TECNOLOGIA", "tipo": "EXPLICITO"}]
        assert corpo["carta"] == "Prezados, ..."
        assert corpo["url_vaga"] == "https://example.com/vaga/1"
        portas["extrator"].extrair.assert_called_once_with(PDF_BYTES)

    def test_sem_cargo_e_empresa_usa_dados_da_vaga(self, client: TestClient):
        response = client.post(URL, json=_payload(pdf_base64=base64.b64encode(PDF_BYTES).decode()))

        assert "BackendEngineer" in response.json()["nome_arquivo"]
        assert "Olist" in response.json()["nome_arquivo"]

    def test_com_perfil_estruturado_nao_extrai_pdf(
        self,
        client: TestClient,
        portas: dict[str, Mock],
        repositorio_perfil: PerfilEstruturadoRepositoryFake,
    ):
        repositorio_perfil.salvar(_perfil())

        response = client.post(URL, json=_payload(perfil_identificador="adriano", cargo_alvo="Engenheiro"))

        assert response.status_code == 200
        portas["extrator"].extrair.assert_not_called()
        curriculo_usado = portas["gerador_pdf"].gerar.call_args.args[0]
        assert curriculo_usado.nome_completo == "Adriano Teixeira"

    def test_perfil_estruturado_inexistente_retorna_422(self, client: TestClient):
        response = client.post(URL, json=_payload(perfil_identificador="inexistente"))

        assert response.status_code == 422
        assert response.json()["detail"] == "Perfil estruturado não encontrado."

    def test_sem_fonte_de_curriculo_retorna_422(self, client: TestClient, portas: dict[str, Mock]):
        response = client.post(URL, json=_payload())

        assert response.status_code == 422
        assert "currículo" in response.json()["detail"]
        portas["gerador_pdf"].gerar.assert_not_called()

    def test_fonte_invalida_retorna_422(self, client: TestClient):
        payload = _payload(pdf_base64=base64.b64encode(PDF_BYTES).decode())
        payload["vaga"]["fonte"] = "LINKEDIN"

        response = client.post(URL, json=payload)

        assert response.status_code == 422

    def test_documentado_no_openapi(self, client: TestClient):
        operacao = client.get("/openapi.json").json()["paths"][URL]["post"]

        assert operacao["summary"] == "Candidatar em vaga externa"
        assert "422" in operacao["responses"]

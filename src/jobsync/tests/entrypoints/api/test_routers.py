"""Testes dos routers FastAPI com TestClient."""

from __future__ import annotations

import base64
import uuid
from datetime import datetime
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.ats_score import ResultadoAtsScore
from jobsync.candidatura.adapters.candidatura_repository_fake import (
    CandidaturaRepositoryFake,
)
from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import (
    AdaptarCurriculoParaVagaOutputDto,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.service import (
    AdaptarCurriculoParaVaga,
)
from jobsync.curriculo.service_layer.analisar_ats_vaga import AnalisarAtsVagaOutputDto
from jobsync.curriculo.service_layer.analisar_ats_vaga.service import AnalisarAtsVaga
from jobsync.curriculo_salvo.adapters.curriculo_salvo_repository_fake import (
    CurriculoSalvoRepositoryFake,
)
from jobsync.curriculo_salvo.domain.curriculo_salvo import CurriculoSalvo
from jobsync.entrypoints.api.dependencies import (
    obter_repositorio_candidatura,
    obter_repositorio_curriculo_salvo,
    obter_repositorio_perfil,
    obter_repositorio_vaga,
    obter_service_adaptar_curriculo,
    obter_service_analisar_ats_vaga,
    obter_service_descobrir_vagas_com_match,
)
from jobsync.entrypoints.api.main import app
from jobsync.perfil.adapters.perfil_repository_fake import PerfilRepositoryFake
from jobsync.shared_kernel.domain import NomeArquivo
from jobsync.vaga import AnaliseVaga
from jobsync.vaga.adapters.vaga_repository_fake import VagaRepositoryFake
from jobsync.vaga_externa import FonteVagaExterna, VagaComScore, VagaExterna
from jobsync.vaga_externa.service_layer.descobrir_vagas_com_match.service import (
    DescobrirVagasComMatch,
)


PDF_BYTES = b"%PDF-1.4 test"
PDF_BASE64 = base64.b64encode(PDF_BYTES).decode()


def _criar_curriculo() -> Curriculo:
    return Curriculo(
        nome_completo="Matheus Silva",
        email="matheus@email.com",
        linkedin="https://linkedin.com/in/matheus",
        secoes=(
            SecaoCurriculo(
                tipo=TipoSecao.TECNOLOGIAS,
                titulo="Tecnologias",
                conteudo="Python",
            ),
        ),
    )


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    overrides = {
        obter_repositorio_curriculo_salvo: lambda: CurriculoSalvoRepositoryFake(),
        obter_repositorio_vaga: lambda: VagaRepositoryFake(),
        obter_repositorio_candidatura: lambda: CandidaturaRepositoryFake(),
        obter_repositorio_perfil: lambda: PerfilRepositoryFake(),
    }
    for original, override in overrides.items():
        app.dependency_overrides[original] = override

    yield TestClient(app)

    app.dependency_overrides.clear()


class TestRoutersBase:
    def test_health(self, client: TestClient):
        response = client.get("/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCurriculoRouter:
    def test_post_curriculo(self, client: TestClient):
        response = client.post(
            "/v1/curriculos",
            json={
                "perfil_identificador": "matheus",
                "nome_referencia": "Curriculo.pdf",
                "pdf_base64": PDF_BASE64,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["perfil_identificador"] == "matheus"
        assert data["nome_referencia"] == "Curriculo.pdf"
        assert "Location" in response.headers

    def test_get_curriculo(self, client: TestClient):
        response = client.get("/v1/curriculos/curriculo-123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "curriculo-123"

    def test_post_adaptar_curriculo(self, client: TestClient):
        class FakeAdaptar:
            def executar(self, input_dto):
                return AdaptarCurriculoParaVagaOutputDto(
                    pdf_bytes=b"%PDF-1.4 adapted",
                    nome_arquivo=NomeArquivo.criar(
                        nome_completo="Matheus Silva",
                        cargo="Engenheiro",
                        empresa="TechCorp",
                    ),
                    curriculo_adaptado=_criar_curriculo(),
                    analise_vaga=AnaliseVaga(
                        requisitos=(),
                        ambiguidade=(),
                        texto_original="vaga",
                    ),
                )

        app.dependency_overrides[obter_service_adaptar_curriculo] = FakeAdaptar

        response = client.post(
            "/v1/curriculos/curriculo-123/adaptacoes",
            json={
                "descricao_vaga": "Desenvolvedor Python",
                "idioma_alvo": "pt",
                "cargo_alvo": "Engenheiro",
                "empresa_alvo": "TechCorp",
                "pdf_base64": PDF_BASE64,
            },
        )

        del app.dependency_overrides[obter_service_adaptar_curriculo]

        assert response.status_code == 200
        data = response.json()
        assert data["nome_completo"] == "Matheus Silva"
        assert data["pdf_base64"] == base64.b64encode(b"%PDF-1.4 adapted").decode()

    def test_post_analisar_ats(self, client: TestClient):
        class FakeAnalisar:
            def executar(self, input_dto):
                return AnalisarAtsVagaOutputDto(
                    curriculo=_criar_curriculo(),
                    analise_vaga=AnaliseVaga(
                        requisitos=(),
                        ambiguidade=(),
                        texto_original="vaga",
                    ),
                    resultado_ats=ResultadoAtsScore(
                        nota=85,
                        requisitos_faltantes=(),
                    ),
                    sugestoes=("Incluir Docker",),
                )

        app.dependency_overrides[obter_service_analisar_ats_vaga] = FakeAnalisar

        response = client.post(
            "/v1/curriculos/curriculo-123/analises-ats",
            json={
                "descricao_vaga": "Desenvolvedor Python",
                "pdf_base64": PDF_BASE64,
            },
        )

        del app.dependency_overrides[obter_service_analisar_ats_vaga]

        assert response.status_code == 200
        data = response.json()
        assert data["nota"] == 85
        assert data["sugestoes"] == ["Incluir Docker"]


class TestVagaRouter:
    def test_get_vagas(self, client: TestClient):
        vaga = VagaRepositoryFake().salvar(
            _vaga_fake(perfil_identificador="matheus")
        )
        app.dependency_overrides[obter_repositorio_vaga] = lambda repo=vaga: _repo_com_vaga(
            repo
        )

        response = client.get("/v1/vagas?perfil_identificador=matheus")

        del app.dependency_overrides[obter_repositorio_vaga]

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_post_vaga(self, client: TestClient):
        response = client.post(
            "/v1/vagas",
            json={
                "perfil_identificador": "matheus",
                "texto_descricao": "Desenvolvedor Python",
                "url_origem": "https://example.com",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["perfil_identificador"] == "matheus"
        assert "Location" in response.headers


class TestVagaExternaRouter:
    def test_post_descobrir_vagas(self, client: TestClient):
        class FakeDescobrir:
            def executar(self, termo, pdf_curriculo, dias_maximo=None):
                return (
                    VagaComScore(
                        vaga=VagaExterna(
                            titulo="Dev Python",
                            empresa="TechCorp",
                            descricao="Python job",
                            url="https://example.com/job",
                            fonte=FonteVagaExterna.REMOTEOK,
                            data_publicacao=None,
                        ),
                        resultado_score=ResultadoAtsScore(
                            nota=90,
                            requisitos_faltantes=(),
                        ),
                    ),
                )

        app.dependency_overrides[obter_service_descobrir_vagas_com_match] = FakeDescobrir

        response = client.post(
            "/v1/vagas/descobrir",
            json={
                "termo": "python",
                "pdf_base64": PDF_BASE64,
                "dias_maximo": 30,
            },
        )

        del app.dependency_overrides[obter_service_descobrir_vagas_com_match]

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["nota"] == 90


class TestCandidaturaRouter:
    def test_post_candidatura(self, client: TestClient):
        vaga_repo = VagaRepositoryFake()
        vaga = vaga_repo.salvar(_vaga_fake(perfil_identificador="matheus"))
        app.dependency_overrides[obter_repositorio_vaga] = lambda: vaga_repo

        curriculo_repo = CurriculoSalvoRepositoryFake()
        curriculo = curriculo_repo.salvar(
            CurriculoSalvo(
                id=str(uuid.uuid4()),
                perfil_identificador="matheus",
                nome_referencia="Curriculo.pdf",
                pdf_bytes=PDF_BYTES,
                data_upload=datetime.now(),
            )
        )
        app.dependency_overrides[obter_repositorio_curriculo_salvo] = lambda: curriculo_repo

        response = client.post(
            "/v1/candidaturas",
            json={
                "perfil_identificador": "matheus",
                "vaga_id": vaga.id,
                "curriculo_salvo_id": curriculo.id,
                "empresa": "TechCorp",
                "cargo": "Engenheiro",
            },
        )

        app.dependency_overrides.pop(obter_repositorio_vaga, None)
        app.dependency_overrides.pop(obter_repositorio_curriculo_salvo, None)

        assert response.status_code == 201
        data = response.json()
        assert data["perfil_identificador"] == "matheus"
        assert data["status"] == "APLICADO"

    def test_post_submissao_candidatura(self, client: TestClient):
        vaga_repo = VagaRepositoryFake()
        vaga = vaga_repo.salvar(_vaga_fake(perfil_identificador="matheus"))
        candidatura_repo = CandidaturaRepositoryFake()
        curriculo_repo = CurriculoSalvoRepositoryFake()
        curriculo = curriculo_repo.salvar(
            CurriculoSalvo(
                id=str(uuid.uuid4()),
                perfil_identificador="matheus",
                nome_referencia="Curriculo.pdf",
                pdf_bytes=PDF_BYTES,
                data_upload=datetime.now(),
            )
        )

        from jobsync.candidatura.service_layer.criar_candidatura import (
            CriarCandidatura,
            CriarCandidaturaInputDto,
        )

        service = CriarCandidatura(
            repositorio_candidatura=candidatura_repo,
            repositorio_vaga=vaga_repo,
        )
        candidatura = service.executar(
            CriarCandidaturaInputDto(
                perfil_identificador="matheus",
                vaga_id=vaga.id,
                curriculo_salvo_id=curriculo.id,
                empresa="TechCorp",
                cargo="Engenheiro",
            )
        )

        app.dependency_overrides[obter_repositorio_candidatura] = lambda: candidatura_repo

        response = client.post(
            f"/v1/candidaturas/{candidatura.id}/submissao",
            json={"novo_status": "entrevista"},
        )

        app.dependency_overrides.pop(obter_repositorio_candidatura, None)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ENTREVISTA"


class TestPerfilRouter:
    def test_get_perfis(self, client: TestClient):
        response = client.get("/v1/perfis")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_get_perfil(self, client: TestClient):
        response = client.get("/v1/perfis/matheus")

        assert response.status_code == 200
        data = response.json()
        assert data["identificador"] == "matheus"


def _vaga_fake(perfil_identificador: str):
    from jobsync.vaga.domain.vaga import Vaga

    return Vaga(
        id=str(uuid.uuid4()),
        perfil_identificador=perfil_identificador,
        texto_descricao="Desenvolvedor Python",
        data_captura=datetime.now(),
        url_origem=None,
    )


def _repo_com_vaga(vaga):
    repo = VagaRepositoryFake()
    repo._vagas[vaga.id] = vaga
    return repo

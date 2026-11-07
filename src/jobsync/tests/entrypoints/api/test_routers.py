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
from jobsync.curriculo import (
    AvaliacaoExperiencia,
    Curriculo,
    ExperienciaParaAvaliacao,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.curriculo.service_layer.gerar_pdf_curriculo_revisado import (
    GerarPdfCurriculoRevisadoOutputDto,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import (
    AdaptarCurriculoParaVagaOutputDto,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AvaliacaoExperienciaAdaptadaDto,
    StatusAvaliacaoAutomatica,
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
    obter_repositorio_perfil_estruturado,
    obter_repositorio_vaga,
    obter_service_adaptar_curriculo,
    obter_service_analisar_ats_vaga,
    obter_service_descobrir_vagas_com_match,
    obter_service_gerar_pdf_curriculo_revisado,
)
from jobsync.entrypoints.api.main import app
from jobsync.perfil.adapters.perfil_repository_fake import PerfilRepositoryFake
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)
from jobsync.perfil_estruturado.domain.perfil_estruturado import (
    ExperienciaProfissional,
    PerfilEstruturado,
)
from jobsync.shared_kernel.domain import NomeArquivo
from jobsync.shared_kernel.domain.score_avaliacao import ResultadoDimensaoAvaliacao
from jobsync.vaga import AnaliseVaga, AvaliacaoDescricaoVaga
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


def _criar_rascunho() -> RascunhoCurriculoAdaptado:
    curriculo = _criar_curriculo()
    return RascunhoCurriculoAdaptado(
        nome_completo=curriculo.nome_completo,
        email=curriculo.email,
        linkedin=curriculo.linkedin,
        secoes=curriculo.secoes,
    )


class GerarPdfFake:
    def __init__(self):
        self.input_dto = None

    def executar(self, input_dto):
        self.input_dto = input_dto
        return GerarPdfCurriculoRevisadoOutputDto(
            pdf_bytes=b"%PDF-1.4 adapted",
            nome_arquivo=NomeArquivo.criar(
                nome_completo=input_dto.rascunho.nome_completo,
                cargo=input_dto.cargo_alvo,
                empresa=input_dto.empresa_alvo,
            ),
        )


@pytest.fixture
def gerar_pdf_fake() -> Generator[GerarPdfFake, None, None]:
    fake = GerarPdfFake()
    app.dependency_overrides[obter_service_gerar_pdf_curriculo_revisado] = lambda: fake
    yield fake
    app.dependency_overrides.pop(obter_service_gerar_pdf_curriculo_revisado, None)


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
        curriculo_repo = CurriculoSalvoRepositoryFake()
        curriculo_repo.salvar(
            CurriculoSalvo(
                id="curriculo-123",
                perfil_identificador="matheus",
                nome_referencia="Curriculo.pdf",
                pdf_bytes=PDF_BYTES,
                data_upload=datetime.now(),
            )
        )
        app.dependency_overrides[obter_repositorio_curriculo_salvo] = (
            lambda: curriculo_repo
        )

        response = client.get(
            "/v1/curriculos/curriculo-123?perfil_identificador=matheus"
        )

        app.dependency_overrides.pop(obter_repositorio_curriculo_salvo, None)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "curriculo-123"

    def test_post_adaptar_curriculo(
        self, client: TestClient, gerar_pdf_fake: GerarPdfFake
    ):
        class FakeAdaptar:
            def executar(self, input_dto):
                return AdaptarCurriculoParaVagaOutputDto(
                    rascunho=_criar_rascunho(),
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
        assert data["nome_arquivo"].endswith("-Engenheiro-Techcorp.pdf")
        assert gerar_pdf_fake.input_dto.rascunho == _criar_rascunho()
        assert gerar_pdf_fake.input_dto.idioma_alvo == "pt"

    def test_post_adaptar_curriculo_com_download_devolve_pdf_binario(
        self, client: TestClient, gerar_pdf_fake: GerarPdfFake
    ):
        class FakeAdaptar:
            def executar(self, input_dto):
                return AdaptarCurriculoParaVagaOutputDto(
                    rascunho=_criar_rascunho(),
                    curriculo_adaptado=_criar_curriculo(),
                    analise_vaga=AnaliseVaga(
                        requisitos=(), ambiguidade=(), texto_original="vaga"
                    ),
                )

        app.dependency_overrides[obter_service_adaptar_curriculo] = FakeAdaptar

        response = client.post(
            "/v1/curriculos/curriculo-123/adaptacoes?download=true",
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
        assert response.headers["content-type"] == "application/pdf"
        assert response.content == b"%PDF-1.4 adapted"
        assert "-Engenheiro-Techcorp.pdf" in response.headers["content-disposition"]

    def test_post_adaptar_curriculo_com_perfil_estruturado(
        self, client: TestClient, gerar_pdf_fake: GerarPdfFake
    ):
        repositorio = PerfilEstruturadoRepositoryFake()
        repositorio.salvar(
            PerfilEstruturado(
                perfil_identificador="matheus",
                nome_completo="Matheus Silva",
                email="matheus@email.com",
                linkedin="",
                resumo_profissional="Engenheiro backend.",
                experiencias=(
                    ExperienciaProfissional(
                        empresa="Starian",
                        cargo="Engenheiro de Software",
                        periodo="2021-2024",
                        descricao="Desenvolvi APIs em Python.",
                    ),
                ),
                formacoes=(),
                certificacoes=(),
                idiomas=(),
                tecnologias=("Python",),
            )
        )

        class FakeAdaptar:
            def __init__(self):
                self.input_dto = None

            def executar(self, input_dto):
                self.input_dto = input_dto
                dimensao = ResultadoDimensaoAvaliacao(
                    score=80, nivel="adequado", confianca=0.9
                )
                return AdaptarCurriculoParaVagaOutputDto(
                    rascunho=_criar_rascunho(),
                    curriculo_adaptado=_criar_curriculo(),
                    analise_vaga=AnaliseVaga(
                        requisitos=(),
                        ambiguidade=(),
                        texto_original="vaga",
                    ),
                    avaliacao_vaga=AvaliacaoDescricaoVaga(
                        completude=dimensao,
                        clareza=dimensao,
                        relevancia=dimensao,
                        inclusao=dimensao,
                    ),
                    status_avaliacao_vaga=StatusAvaliacaoAutomatica.AVALIADA,
                    avaliacoes_experiencias=(
                        AvaliacaoExperienciaAdaptadaDto(
                            experiencia=input_dto.experiencias_profissionais[0],
                            status=StatusAvaliacaoAutomatica.AVALIADA,
                            avaliacao=AvaliacaoExperiencia(
                                clareza_escrita=dimensao,
                                qualidade_detalhe=dimensao,
                                aderencia_vaga=dimensao,
                                consistencia_textual=dimensao,
                            ),
                        ),
                    ),
                )

        fake_adaptar = FakeAdaptar()
        app.dependency_overrides[obter_service_adaptar_curriculo] = (
            lambda: fake_adaptar
        )
        app.dependency_overrides[obter_repositorio_perfil_estruturado] = (
            lambda: repositorio
        )

        response = client.post(
            "/v1/curriculos/curriculo-123/adaptacoes",
            json={
                "descricao_vaga": "Desenvolvedor Python",
                "idioma_alvo": "pt",
                "cargo_alvo": "Engenheiro",
                "empresa_alvo": "TechCorp",
                "perfil_identificador": "matheus",
            },
        )

        app.dependency_overrides.pop(obter_service_adaptar_curriculo, None)
        app.dependency_overrides.pop(obter_repositorio_perfil_estruturado, None)

        assert response.status_code == 200
        assert fake_adaptar.input_dto is not None
        experiencias = fake_adaptar.input_dto.experiencias_profissionais
        assert len(experiencias) == 1
        assert experiencias[0].cargo == "Engenheiro de Software"
        assert experiencias[0].empresa == "Starian"
        assert experiencias[0].periodo == "2021-2024"

        data = response.json()
        assert data["nome_completo"] == "Matheus Silva"
        assert data["status_avaliacao_vaga"] == "avaliada"
        assert data["avaliacao_vaga"]["score"] == 80
        assert data["avaliacoes_experiencias"][0]["status"] == "avaliada"
        assert data["avaliacoes_experiencias"][0]["avaliacao"]["score"] == 80
        assert (
            data["avaliacoes_experiencias"][0]["experiencia"]["empresa"] == "Starian"
        )

    def test_post_rascunho_adaptado_devolve_rascunho_sem_pdf(
        self, client: TestClient, gerar_pdf_fake: GerarPdfFake
    ):
        class FakeAdaptar:
            def executar(self, input_dto):
                return AdaptarCurriculoParaVagaOutputDto(
                    rascunho=_criar_rascunho(),
                    curriculo_adaptado=_criar_curriculo(),
                    analise_vaga=AnaliseVaga(
                        requisitos=(), ambiguidade=(), texto_original="vaga"
                    ),
                )

        app.dependency_overrides[obter_service_adaptar_curriculo] = FakeAdaptar

        response = client.post(
            "/v1/curriculos/curriculo-123/rascunhos-adaptados",
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
        assert "pdf_base64" not in data
        assert data["analise_vaga"] == {
            "requisitos": [],
            "ambiguidade": [],
            "texto_original": "vaga",
        }
        assert data["rascunho"]["nome_completo"] == "Matheus Silva"
        assert data["rascunho"]["secoes"] == [
            {"tipo": "TECNOLOGIAS", "titulo": "Tecnologias", "conteudo": "Python"}
        ]
        assert data["rascunho"]["experiencias"] is None
        assert gerar_pdf_fake.input_dto is None

    def test_post_rascunho_adaptado_com_entrada_invalida_devolve_422(
        self, client: TestClient
    ):
        class FakeAdaptar:
            def executar(self, input_dto):
                raise ValueError("A descrição da vaga é obrigatória.")

        app.dependency_overrides[obter_service_adaptar_curriculo] = FakeAdaptar

        response = client.post(
            "/v1/curriculos/curriculo-123/rascunhos-adaptados",
            json={
                "descricao_vaga": " ",
                "idioma_alvo": "pt",
                "cargo_alvo": "Engenheiro",
                "empresa_alvo": "TechCorp",
                "pdf_base64": PDF_BASE64,
            },
        )

        del app.dependency_overrides[obter_service_adaptar_curriculo]

        assert response.status_code == 422

    def test_post_curriculo_revisado_gera_pdf_do_rascunho_editado(
        self, client: TestClient, gerar_pdf_fake: GerarPdfFake
    ):
        response = client.post(
            "/v1/curriculos-revisados",
            json={
                "rascunho": {
                    "nome_completo": "Matheus Editado",
                    "email": "matheus@email.com",
                    "linkedin": "",
                    "secoes": [
                        {"tipo": "PERFIL", "titulo": "Perfil", "conteudo": "Resumo editado."}
                    ],
                    "experiencias": [
                        {
                            "cargo": "Dev",
                            "empresa": "TechCorp",
                            "periodo": "2024",
                            "conquistas": ["Texto editado."],
                            "contexto": "Contexto editado.",
                        }
                    ],
                },
                "idioma_alvo": "pt",
                "cargo_alvo": "Engenheiro",
                "empresa_alvo": "TechCorp",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pdf_base64"] == base64.b64encode(b"%PDF-1.4 adapted").decode()
        assert data["nome_arquivo"].startswith("MatheusEditado-")
        rascunho = gerar_pdf_fake.input_dto.rascunho
        assert rascunho.secoes[0].conteudo == "Resumo editado."
        assert rascunho.experiencias[0].conquistas == ("Texto editado.",)
        assert rascunho.experiencias[0].contexto == "Contexto editado."

    def test_post_curriculo_revisado_com_download_devolve_pdf_binario(
        self, client: TestClient, gerar_pdf_fake: GerarPdfFake
    ):
        response = client.post(
            "/v1/curriculos-revisados?download=true",
            json={
                "rascunho": {
                    "nome_completo": "Matheus Silva",
                    "secoes": [
                        {"tipo": "PERFIL", "titulo": "Perfil", "conteudo": "Resumo."}
                    ],
                },
                "idioma_alvo": "pt",
                "cargo_alvo": "Engenheiro",
                "empresa_alvo": "TechCorp",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content == b"%PDF-1.4 adapted"

    def test_post_curriculo_revisado_com_rascunho_invalido_devolve_422(
        self, client: TestClient, gerar_pdf_fake: GerarPdfFake
    ):
        response = client.post(
            "/v1/curriculos-revisados",
            json={
                "rascunho": {
                    "nome_completo": "Matheus Silva",
                    "secoes": [],
                    "experiencias": [{"cargo": "", "empresa": "TechCorp", "conquistas": ["x"]}],
                },
                "idioma_alvo": "pt",
                "cargo_alvo": "Engenheiro",
                "empresa_alvo": "TechCorp",
            },
        )

        assert response.status_code == 422
        assert gerar_pdf_fake.input_dto is None

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

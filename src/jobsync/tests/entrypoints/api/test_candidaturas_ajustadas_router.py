import base64
import os
import sqlite3
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.candidatura.adapters import CandidaturaRepositoryImpl
from jobsync.candidatura.adapters.candidatura_repository_fake import CandidaturaRepositoryFake
from jobsync.curriculo_salvo.adapters.curriculo_salvo_repository_fake import CurriculoSalvoRepositoryFake
from jobsync.curriculo_salvo.adapters.curriculo_salvo_repository_impl import CurriculoSalvoRepositoryImpl
from jobsync.curriculo_salvo.domain.limite_curriculos_salvos import LIMITE_CURRICULOS_POR_PERFIL
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import (
    obter_repositorio_candidatura,
    obter_repositorio_curriculo_salvo,
    obter_repositorio_vaga,
)
from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl
from jobsync.vaga.adapters.vaga_repository_fake import VagaRepositoryFake
from jobsync.vaga.adapters.vaga_repository_impl import VagaRepositoryImpl

PDF = b"%PDF-1.4 curriculo-gerado"
URL = "/v1/candidaturas-ajustadas"


def _corpo(**alteracoes) -> dict:
    return {
        "perfil_identificador": "ana",
        "cargo": "Engenheiro de Software",
        "empresa": "TechCorp",
        "descricao_vaga": "Vaga de engenharia de software backend.",
        "nome_arquivo": "AnaSouza-2026-11-09-Engenheiro-TechCorp.pdf",
        "pdf_base64": base64.b64encode(PDF).decode(),
        **alteracoes,
    }


def _usar(candidaturas, vagas, curriculos) -> None:
    app.dependency_overrides[obter_repositorio_candidatura] = lambda: candidaturas
    app.dependency_overrides[obter_repositorio_vaga] = lambda: vagas
    app.dependency_overrides[obter_repositorio_curriculo_salvo] = lambda: curriculos


def _soltar() -> None:
    for dependencia in (obter_repositorio_candidatura, obter_repositorio_vaga, obter_repositorio_curriculo_salvo):
        app.dependency_overrides.pop(dependencia, None)


@pytest.fixture
def candidaturas() -> CandidaturaRepositoryFake:
    return CandidaturaRepositoryFake()


class VagaRepositoryEspiao(VagaRepositoryFake):
    def __init__(self) -> None:
        super().__init__()
        self.salvas: list[str] = []
        self.convertidas: list[str] = []

    def salvar(self, vaga):
        self.salvas.append(vaga.id)
        return super().salvar(vaga)

    def marcar_como_convertida(self, vaga_id: str) -> None:
        self.convertidas.append(vaga_id)
        super().marcar_como_convertida(vaga_id)


@pytest.fixture
def vagas() -> VagaRepositoryEspiao:
    return VagaRepositoryEspiao()


@pytest.fixture
def curriculos() -> CurriculoSalvoRepositoryFake:
    return CurriculoSalvoRepositoryFake()


@pytest.fixture
def client(candidaturas, vagas, curriculos) -> Generator[TestClient, None, None]:
    _usar(candidaturas, vagas, curriculos)
    yield TestClient(app)
    _soltar()


class TestCandidaturasAjustadasRouter:
    def test_confirmar_retorna_201_com_a_candidatura_aplicada(self, client: TestClient):
        response = client.post(URL, json=_corpo())

        corpo = response.json()
        assert response.status_code == 201
        assert corpo["status"] == "APLICADO"
        assert corpo["empresa"] == "TechCorp"
        assert corpo["cargo"] == "Engenheiro de Software"
        assert corpo["perfil_identificador"] == "ana"
        assert corpo["curriculo_salvo_id"]
        assert corpo["vaga_id"]
        assert [mudanca["status"] for mudanca in corpo["historico_status"]] == ["APLICADO"]

    def test_candidatura_confirmada_aparece_no_board_em_aplicado(self, client: TestClient):
        criada = client.post(URL, json=_corpo()).json()

        listagem = client.get("/v1/candidaturas", params={"perfil_identificador": "ana"}).json()

        assert [c["id"] for c in listagem["por_status"]["APLICADO"]] == [criada["id"]]

    def test_pdf_gerado_fica_na_biblioteca_ligado_a_candidatura(self, client: TestClient, curriculos):
        criada = client.post(URL, json=_corpo()).json()

        salvos = curriculos.listar_por_perfil("ana")
        assert [c.id for c in salvos] == [criada["curriculo_salvo_id"]]
        assert salvos[0].pdf_bytes == PDF
        assert salvos[0].nome_referencia == "AnaSouza-2026-11-09-Engenheiro-TechCorp.pdf"

    def test_vaga_ligada_a_candidatura_fica_convertida_e_fora_de_vagas_salvas(self, client: TestClient, vagas):
        criada = client.post(URL, json=_corpo()).json()

        assert vagas.salvas == [criada["vaga_id"]]
        assert vagas.convertidas == [criada["vaga_id"]]
        assert vagas.listar_nao_convertidas("ana") == ()

    def test_biblioteca_cheia_retorna_409_problem_details_e_nao_grava_nada(
        self, client: TestClient, candidaturas, vagas, curriculos
    ):
        for indice in range(LIMITE_CURRICULOS_POR_PERFIL):
            assert client.post(URL, json=_corpo(nome_arquivo=f"cv{indice}.pdf")).status_code == 201
        candidaturas_antes = len(candidaturas.listar_por_perfil("ana"))

        response = client.post(URL, json=_corpo(nome_arquivo="cv-extra.pdf"))

        corpo = response.json()
        assert response.status_code == 409
        assert corpo["status"] == 409
        assert corpo["type"] == "https://jobsync.com/erros/limite-curriculos-salvos"
        assert corpo["detail"] == (
            "Sua biblioteca de currículos está cheia. Remova um currículo para confirmar a candidatura."
        )
        assert len(candidaturas.listar_por_perfil("ana")) == candidaturas_antes
        assert len(curriculos.listar_por_perfil("ana")) == LIMITE_CURRICULOS_POR_PERFIL

    @pytest.mark.parametrize(
        ("alteracao", "trecho_da_mensagem"),
        [
            ({"empresa": "  "}, "empresa"),
            ({"cargo": ""}, "cargo"),
            ({"descricao_vaga": ""}, "descrição"),
            ({"nome_arquivo": " "}, "nome do arquivo"),
            ({"pdf_base64": base64.b64encode(b"nao e um pdf").decode()}, "não é um PDF"),
            ({"pdf_base64": "isto não é base64!!"}, "base64"),
            ({"pdf_base64": ""}, "PDF"),
        ],
    )
    def test_dados_invalidos_retornam_422_com_mensagem_e_nao_gravam_nada(
        self, client: TestClient, candidaturas, vagas, curriculos, alteracao, trecho_da_mensagem
    ):
        response = client.post(URL, json=_corpo(**alteracao))

        assert response.status_code == 422
        assert trecho_da_mensagem in response.json()["detail"]
        assert candidaturas.listar_por_perfil("ana") == ()
        assert vagas.listar_nao_convertidas("ana") == ()
        assert curriculos.listar_por_perfil("ana") == ()

    def test_campo_ausente_retorna_422_de_validacao(self, client: TestClient):
        corpo = _corpo()
        del corpo["empresa"]

        response = client.post(URL, json=corpo)

        assert response.status_code == 422
        assert "empresa" in response.json()["detail"]


@pytest.fixture
def caminho_banco() -> Generator[str, None, None]:
    fd, caminho = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield caminho
    os.remove(caminho)


class TestCandidaturasAjustadasComSqlite:
    def test_registros_ficam_ligados_por_chave_estrangeira_no_banco_real(self, caminho_banco: str):
        PerfilRepositoryImpl(caminho_banco=caminho_banco).criar("ana")
        _usar(
            CandidaturaRepositoryImpl(caminho_banco=caminho_banco),
            VagaRepositoryImpl(caminho_banco=caminho_banco),
            CurriculoSalvoRepositoryImpl(caminho_banco=caminho_banco),
        )
        try:
            client = TestClient(app)

            response = client.post(URL, json=_corpo())
            listagem = client.get("/v1/candidaturas", params={"perfil_identificador": "ana"}).json()
        finally:
            _soltar()

        conexao = sqlite3.connect(caminho_banco)
        try:
            violacoes = conexao.execute("PRAGMA foreign_key_check").fetchall()
            total_de_vagas = conexao.execute("SELECT COUNT(*) FROM vaga").fetchone()[0]
            vagas_pendentes = conexao.execute("SELECT COUNT(*) FROM vaga WHERE convertida_em_candidatura = 0").fetchone()[0]
        finally:
            conexao.close()
        assert response.status_code == 201
        assert [c["id"] for c in listagem["por_status"]["APLICADO"]] == [response.json()["id"]]
        assert violacoes == []
        assert total_de_vagas == 1
        assert vagas_pendentes == 0

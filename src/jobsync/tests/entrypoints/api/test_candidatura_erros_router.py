from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from jobsync.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from jobsync.candidatura.adapters.candidatura_repository_fake import CandidaturaRepositoryFake
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_repositorio_candidatura, obter_repositorio_vaga
from jobsync.vaga.adapters.vaga_repository_fake import VagaRepositoryFake


def _candidatura(**alteracoes) -> dict:
    return {
        "perfil_identificador": "adriano",
        "vaga_id": "vaga-1",
        "curriculo_salvo_id": "cv-1",
        "empresa": "Olist",
        "cargo": "Backend",
        **alteracoes,
    }


def _salva(repositorio: CandidaturaRepositoryFake) -> str:
    agora = datetime(2026, 11, 6, 10, 0)
    repositorio.salvar(
        Candidatura(
            id="cand-1",
            perfil_identificador="adriano",
            vaga_id="vaga-1",
            curriculo_salvo_id="cv-1",
            empresa="Olist",
            cargo="Backend",
            status=StatusCandidatura.APLICADO,
            data_aplicacao=agora,
            historico_status=(MudancaStatus(StatusCandidatura.APLICADO, agora),),
        )
    )
    return "cand-1"


@pytest.fixture
def candidaturas() -> CandidaturaRepositoryFake:
    return CandidaturaRepositoryFake()


@pytest.fixture
def client(candidaturas: CandidaturaRepositoryFake) -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_repositorio_candidatura] = lambda: candidaturas
    app.dependency_overrides[obter_repositorio_vaga] = lambda: VagaRepositoryFake()

    yield TestClient(app)

    app.dependency_overrides.pop(obter_repositorio_candidatura, None)
    app.dependency_overrides.pop(obter_repositorio_vaga, None)


class TestCandidaturaErrosRouter:
    def test_criar_sem_curriculo_retorna_422_com_mensagem(self, client: TestClient):
        response = client.post("/v1/candidaturas", json=_candidatura(curriculo_salvo_id=" "))

        assert response.status_code == 422
        assert response.json()["detail"] == "O currículo salvo usado é obrigatório."

    def test_mover_para_status_invalido_retorna_422(self, client: TestClient, candidaturas: CandidaturaRepositoryFake):
        candidatura_id = _salva(candidaturas)

        response = client.post(f"/v1/candidaturas/{candidatura_id}/submissao", json={"novo_status": "contratado"})

        assert response.status_code == 422
        assert "aplicado, entrevista, oferta, rejeitado" in response.json()["detail"]

    def test_mover_aceita_status_em_maiusculas(self, client: TestClient, candidaturas: CandidaturaRepositoryFake):
        candidatura_id = _salva(candidaturas)

        response = client.post(f"/v1/candidaturas/{candidatura_id}/submissao", json={"novo_status": "OFERTA"})

        assert response.status_code == 200
        assert response.json()["status"] == "OFERTA"

    def test_mover_candidatura_inexistente_retorna_404(self, client: TestClient):
        response = client.post("/v1/candidaturas/nao-existe/submissao", json={"novo_status": "entrevista"})

        assert response.status_code == 404
        assert response.json()["detail"] == "Candidatura não encontrada."

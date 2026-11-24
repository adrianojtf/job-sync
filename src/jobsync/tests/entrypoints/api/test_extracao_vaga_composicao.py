from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.dependencies import (
    obter_configuracao_leitura_vaga,
    obter_limitador_leitura_vaga,
)
from jobsync.entrypoints.api.main import app

TEXTO = "Engenheiro de Software na Empresa X. Remoto. Python e FastAPI."


def _limpar_caches() -> None:
    obter_configuracao_leitura_vaga.cache_clear()
    obter_limitador_leitura_vaga.cache_clear()


@pytest.fixture
def client(monkeypatch) -> Generator[TestClient, None, None]:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("VAGA_LEITURA_LIMITE_POR_MINUTO", "2")
    _limpar_caches()
    yield TestClient(app)
    _limpar_caches()


class TestComposicaoDaExtracaoDeVaga:
    def test_texto_sem_chave_da_ia_devolve_apenas_a_descricao(self, client: TestClient):
        response = client.post("/v1/vagas/extracoes", json={"texto": TEXTO})

        assert response.status_code == 200
        corpo = response.json()
        assert corpo["descricao"] == TEXTO
        assert corpo["cargo"] is None
        assert corpo["empresa"] is None

    def test_o_limite_vale_entre_requisicoes_e_vem_do_ambiente(self, client: TestClient):
        for _ in range(2):
            assert client.post("/v1/vagas/extracoes", json={"texto": TEXTO}).status_code == 200

        response = client.post("/v1/vagas/extracoes", json={"texto": TEXTO})

        assert response.status_code == 429
        assert int(response.headers["Retry-After"]) >= 1
        assert response.json()["type"].endswith("/limite-leitura-vaga")

    def test_o_limitador_e_unico_por_processo(self, client: TestClient):
        assert obter_limitador_leitura_vaga() is obter_limitador_leitura_vaga()

    def test_link_do_linkedin_com_a_leitura_desligada_pede_o_texto(self, client: TestClient, monkeypatch):
        monkeypatch.setenv("VAGA_LEITURA_LINKEDIN_HABILITADA", "false")
        _limpar_caches()

        response = client.post("/v1/vagas/extracoes", json={"url": "https://www.linkedin.com/jobs/view/4484559483/"})

        assert response.status_code == 422
        assert response.json()["type"].endswith("/fonte-vaga-nao-suportada")
        assert "texto da vaga" in response.json()["detail"].lower()

    def test_link_do_linkedin_sem_vaga_especifica_devolve_422(self, client: TestClient):
        response = client.post("/v1/vagas/extracoes", json={"url": "https://www.linkedin.com/jobs/search/?keywords=python"})

        assert response.status_code == 422
        assert response.json()["type"].endswith("/link-vaga-invalido")

    @pytest.mark.parametrize(
        "url",
        ["http://127.0.0.1/vaga", "http://169.254.169.254/latest/meta-data/", "http://[::1]:8000/", "http://10.0.0.5/vaga"],
    )
    def test_enderecos_internos_sao_recusados_sem_acesso_a_rede(self, client: TestClient, url: str):
        response = client.post("/v1/vagas/extracoes", json={"url": url})

        assert response.status_code == 502
        assert response.json()["type"].endswith("/leitura-vaga-indisponivel")
        assert "texto da vaga" in response.json()["detail"].lower()

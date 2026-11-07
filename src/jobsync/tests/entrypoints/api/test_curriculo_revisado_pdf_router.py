"""Testes de ponta a ponta de POST /v1/curriculos-revisados com o gerador de PDF real."""
import base64
import io

import pdfplumber
import pytest
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _corpo(idioma: str, **experiencia) -> dict:
    return {
        "rascunho": {
            "nome_completo": "Ana Souza",
            "secoes": [],
            "experiencias": [{"cargo": "Dev", "empresa": "TechCorp", "periodo": "2024", **experiencia}],
        },
        "idioma_alvo": idioma,
        "cargo_alvo": "Engenheira",
        "empresa_alvo": "TechCorp",
    }


def _pagina(response):
    pdf = base64.b64decode(response.json()["pdf_base64"])
    with pdfplumber.open(io.BytesIO(pdf)) as documento:
        pagina = documento.pages[0]
        return pagina.extract_text(), [c for c in pagina.chars if c["text"].strip()]


@pytest.mark.parametrize(("idioma", "rotulo"), [("pt", "Contexto"), ("en", "Context")])
def test_pdf_traz_as_conquistas_e_o_contexto_editados_no_rotulo_do_idioma(client, idioma, rotulo):
    response = client.post(
        "/v1/curriculos-revisados",
        json=_corpo(idioma, conquistas=["Criei APIs.", "Reduzi custos."], contexto="Empresa de pagamentos."),
    )

    texto, _ = _pagina(response)

    assert response.status_code == 200
    assert "Dev — TechCorp (2024)" in texto
    assert "Criei APIs." in texto
    assert "Reduzi custos." in texto
    assert f"{rotulo}: Empresa de pagamentos." in texto


def test_pdf_sem_contexto_nao_traz_rotulo(client):
    response = client.post("/v1/curriculos-revisados", json=_corpo("pt", conquistas=["Criei APIs."]))

    texto, _ = _pagina(response)

    assert "Contexto" not in texto


def test_descricao_legada_e_rejeitada_com_422_em_vez_de_perder_o_conteudo(client):
    response = client.post(
        "/v1/curriculos-revisados", json=_corpo("pt", descricao="- Criei APIs.\nReduzi custos.")
    )

    assert response.status_code == 422
    assert "descricao" in response.json()["detail"]

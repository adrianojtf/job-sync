"""Contrato do rascunho: o que a adaptação devolve é aceito como veio pela geração do PDF."""
import base64
import io
from collections.abc import Generator
from unittest.mock import Mock

import pdfplumber
import pytest
from fastapi.testclient import TestClient

from jobsync.curriculo import (
    AjustadorExperienciaPort,
    AjustadorTextoPort,
    EquivalenciaTecnologia,
    ExperienciaAdaptada,
    ExtratorCurriculoPort,
    IdentificadorEquivalenciasPort,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import AdaptarCurriculoParaVaga
from jobsync.entrypoints.api.dependencies import (
    obter_repositorio_perfil_estruturado,
    obter_service_adaptar_curriculo,
)
from jobsync.entrypoints.api.main import app
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)
from jobsync.perfil_estruturado.domain.perfil_estruturado import (
    ExperienciaProfissional,
    PerfilEstruturado,
)
from jobsync.vaga import AnaliseVaga
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort

CONQUISTAS_DA_IA = ("Criei APIs em Python.", "Reduzi custos em 30%.")
CONTEXTO_DA_IA = "Plataforma de pagamentos usada por milhares de pessoas."


def _servico_de_adaptacao() -> AdaptarCurriculoParaVaga:
    analisador = Mock(spec=JobDescriptionAnalyzerPort)
    analisador.analisar.return_value = AnaliseVaga(
        requisitos=(), ambiguidade=(), texto_original="Vaga Python"
    )
    ajustador_texto = Mock(spec=AjustadorTextoPort)
    ajustador_texto.ajustar_secao.side_effect = lambda secao, **_: secao
    ajustador_experiencia = Mock(spec=AjustadorExperienciaPort)
    ajustador_experiencia.ajustar.side_effect = lambda experiencia, **_: ExperienciaAdaptada(
        cargo=experiencia.cargo,
        empresa=experiencia.empresa,
        periodo=experiencia.periodo,
        conquistas=CONQUISTAS_DA_IA,
        contexto=CONTEXTO_DA_IA,
    )
    identificador = Mock(spec=IdentificadorEquivalenciasPort)
    identificador.identificar.return_value = (EquivalenciaTecnologia(original="Python", alvo="Kotlin"),)
    return AdaptarCurriculoParaVaga(
        extrator=Mock(spec=ExtratorCurriculoPort),
        analisador_vaga=analisador,
        ajustador_texto=ajustador_texto,
        ajustador_experiencia=ajustador_experiencia,
        identificador_equivalencias=identificador,
    )


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    repositorio = PerfilEstruturadoRepositoryFake()
    repositorio.salvar(
        PerfilEstruturado(
            perfil_identificador="ana",
            nome_completo="Ana Souza",
            email="ana@example.com",
            linkedin="",
            resumo_profissional="Engenheira backend.",
            experiencias=(
                ExperienciaProfissional(
                    empresa="TechCorp",
                    cargo="Engenheira de Software",
                    periodo="2022 - Atual",
                    descricao="Fiz APIs em Python.",
                ),
            ),
            formacoes=(),
            certificacoes=(),
            idiomas=(),
            tecnologias=("Python",),
        )
    )
    app.dependency_overrides[obter_repositorio_perfil_estruturado] = lambda: repositorio
    app.dependency_overrides[obter_service_adaptar_curriculo] = _servico_de_adaptacao
    yield TestClient(app)
    app.dependency_overrides.pop(obter_repositorio_perfil_estruturado, None)
    app.dependency_overrides.pop(obter_service_adaptar_curriculo, None)


def _gerar_rascunho(client: TestClient, idioma: str = "en") -> dict:
    response = client.post(
        "/v1/curriculos/perfil-estruturado/rascunhos-adaptados",
        json={
            "descricao_vaga": "Vaga Python",
            "idioma_alvo": idioma,
            "cargo_alvo": "Engenheira",
            "empresa_alvo": "Globex",
            "perfil_identificador": "ana",
        },
    )
    assert response.status_code == 200
    return response.json()["rascunho"]


def _confirmar(client: TestClient, rascunho: dict, idioma: str = "en"):
    response = client.post(
        "/v1/curriculos-revisados",
        json={
            "rascunho": rascunho,
            "idioma_alvo": idioma,
            "cargo_alvo": "Engenheira",
            "empresa_alvo": "Globex",
        },
    )
    assert response.status_code == 200
    with pdfplumber.open(io.BytesIO(base64.b64decode(response.json()["pdf_base64"]))) as pdf:
        pagina = pdf.pages[0]
        return pagina.extract_text(), pagina


def test_o_rascunho_traz_conquistas_e_contexto_gerados_pela_ia(client):
    rascunho = _gerar_rascunho(client)

    assert rascunho["experiencias"] == [
        {
            "cargo": "Engenheira de Software",
            "empresa": "TechCorp",
            "periodo": "2022 - Atual",
            "conquistas": list(CONQUISTAS_DA_IA),
            "contexto": CONTEXTO_DA_IA,
        }
    ]


def test_o_rascunho_lista_as_trocas_de_tecnologia_com_a_experiencia(client):
    rascunho = _gerar_rascunho(client)

    assert rascunho["ajustes_tecnologia"] == [
        {
            "indice_experiencia": 0,
            "cargo": "Engenheira de Software",
            "empresa": "TechCorp",
            "original": "Python",
            "alvo": "Kotlin",
        }
    ]


def test_o_rascunho_devolvido_e_aceito_como_veio_e_o_pdf_traz_o_padrao(client):
    rascunho = _gerar_rascunho(client)

    texto, pagina = _confirmar(client, rascunho)

    assert "TechCorp 2022 - Atual\nEngenheira de Software\n" in texto
    assert "Criei APIs em Python." in texto
    assert "Reduzi custos em 30%." in texto
    assert f"Context: {CONTEXTO_DA_IA}" in texto
    palavra = next(p for p in pagina.extract_words() if p["text"] == "Context:")
    letras = [c for c in pagina.chars if c["text"].strip() and abs(c["top"] - palavra["top"]) < 1]
    assert all(c["fontname"].endswith("Carlito-Italic") for c in letras)


def test_o_pdf_reflete_o_que_o_usuario_revisou_e_nao_o_texto_bruto_da_ia(client):
    rascunho = _gerar_rascunho(client)
    rascunho["experiencias"][0]["conquistas"] = ["Conquista escrita pelo usuário."]
    rascunho["experiencias"][0]["contexto"] = "Contexto corrigido pelo usuário."

    texto, _ = _confirmar(client, rascunho)

    assert "Conquista escrita pelo usuário." in texto
    assert "Context: Contexto corrigido pelo usuário." in texto
    assert "Criei APIs em Python." not in texto
    assert CONTEXTO_DA_IA not in texto


def test_o_rotulo_do_contexto_segue_o_idioma_da_confirmacao(client):
    rascunho = _gerar_rascunho(client, idioma="pt")

    texto, _ = _confirmar(client, rascunho, idioma="pt")

    assert f"Contexto: {CONTEXTO_DA_IA}" in texto

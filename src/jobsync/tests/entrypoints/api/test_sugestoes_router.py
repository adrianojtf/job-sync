"""Testes dos endpoints de sugestão de IA por seção e por experiência (JOB-0034)."""
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.curriculo import ExperienciaAdaptada, ExperienciaParaAvaliacao, SecaoCurriculo
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel
from jobsync.entrypoints.api.dependencies import (
    obter_service_sugerir_ajuste_experiencia,
    obter_service_sugerir_ajuste_experiencia_adaptada,
    obter_service_sugerir_ajuste_secao_curriculo,
)
from jobsync.entrypoints.api.main import app

CONTEXTO_VAGA = {
    "descricao_vaga": "Vaga Java com Kafka",
    "idioma_alvo": "en",
    "analise_vaga": {
        "requisitos": [{"nome": "Java", "categoria": "TECNOLOGIA", "tipo": "EXPLICITO"}],
        "ambiguidade": [],
        "texto_original": "Vaga Java com Kafka",
    },
}


class ServicoSecaoFake:
    def __init__(self, erro: Exception | None = None):
        self.chamadas: list[tuple] = []
        self._erro = erro

    def executar(self, secao: SecaoCurriculo, contexto):
        self.chamadas.append((secao, contexto))
        if self._erro:
            raise self._erro
        return secao.com_novo_conteudo("Texto sugerido.")


class ServicoExperienciaFake:
    def __init__(self, erro: Exception | None = None):
        self.chamadas: list[ExperienciaParaAvaliacao] = []
        self._erro = erro

    def executar(self, experiencia: ExperienciaParaAvaliacao):
        self.chamadas.append(experiencia)
        if self._erro:
            raise self._erro
        return ExperienciaParaAvaliacao(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            descricao="Descrição sugerida.",
        )


class ServicoExperienciaAdaptadaFake:
    def __init__(self, erro: Exception | None = None):
        self.chamadas: list[tuple] = []
        self._erro = erro

    def executar(self, experiencia: ExperienciaAdaptada, contexto):
        self.chamadas.append((experiencia, contexto))
        if self._erro:
            raise self._erro
        return ExperienciaAdaptada(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            conquistas=("Conquista sugerida.",),
            contexto="Contexto sugerido.",
        )


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    yield TestClient(app)
    app.dependency_overrides.pop(obter_service_sugerir_ajuste_secao_curriculo, None)
    app.dependency_overrides.pop(obter_service_sugerir_ajuste_experiencia, None)
    app.dependency_overrides.pop(obter_service_sugerir_ajuste_experiencia_adaptada, None)


def _sobrescrever_servicos_de_experiencia(perfil=None, adaptada=None):
    perfil = perfil or ServicoExperienciaFake()
    adaptada = adaptada or ServicoExperienciaAdaptadaFake()
    app.dependency_overrides[obter_service_sugerir_ajuste_experiencia] = lambda: perfil
    app.dependency_overrides[obter_service_sugerir_ajuste_experiencia_adaptada] = lambda: adaptada
    return perfil, adaptada


def _corpo_secao(**extras) -> dict:
    return {
        "secao": {"tipo": "PERFIL", "titulo": "Perfil", "conteudo": "Texto atual."},
        **extras,
    }


def _corpo_experiencia(**extras) -> dict:
    return {
        "experiencia": {
            "cargo": "Dev",
            "empresa": "TechCorp",
            "periodo": "2024",
            "descricao": "Descrição atual.",
        },
        **extras,
    }


class TestSugestaoDeSecaoRouter:
    def test_com_contexto_de_vaga_devolve_o_conteudo_sugerido(self, client: TestClient):
        servico = ServicoSecaoFake()
        app.dependency_overrides[obter_service_sugerir_ajuste_secao_curriculo] = lambda: servico

        response = client.post(
            "/v1/secoes-curriculo/sugestoes", json=_corpo_secao(contexto_vaga=CONTEXTO_VAGA)
        )

        assert response.status_code == 200
        assert response.json() == {"conteudo_sugerido": "Texto sugerido."}
        secao, contexto = servico.chamadas[0]
        assert secao.conteudo == "Texto atual."
        assert contexto.idioma_alvo == "en"
        assert contexto.analise_vaga.requisitos[0].nome == "Java"

    def test_sem_contexto_de_vaga_chama_o_servico_sem_contexto(self, client: TestClient):
        servico = ServicoSecaoFake()
        app.dependency_overrides[obter_service_sugerir_ajuste_secao_curriculo] = lambda: servico

        response = client.post("/v1/secoes-curriculo/sugestoes", json=_corpo_secao())

        assert response.status_code == 200
        assert servico.chamadas[0][1] is None

    def test_entrada_invalida_devolve_422(self, client: TestClient):
        servico = ServicoSecaoFake(erro=ValueError("A seção FORMACAO não tem sugestão de IA."))
        app.dependency_overrides[obter_service_sugerir_ajuste_secao_curriculo] = lambda: servico

        response = client.post("/v1/secoes-curriculo/sugestoes", json=_corpo_secao())

        assert response.status_code == 422
        assert "não tem sugestão" in response.json()["detail"]

    def test_conteudo_vazio_devolve_422_sem_chamar_o_servico(self, client: TestClient):
        servico = ServicoSecaoFake()
        app.dependency_overrides[obter_service_sugerir_ajuste_secao_curriculo] = lambda: servico
        corpo = {"secao": {"tipo": "PERFIL", "titulo": "Perfil", "conteudo": "  "}}

        response = client.post("/v1/secoes-curriculo/sugestoes", json=corpo)

        assert response.status_code == 422
        assert servico.chamadas == []

    def test_ia_indisponivel_devolve_502(self, client: TestClient):
        servico = ServicoSecaoFake(erro=SugestaoIAIndisponivel())
        app.dependency_overrides[obter_service_sugerir_ajuste_secao_curriculo] = lambda: servico

        response = client.post("/v1/secoes-curriculo/sugestoes", json=_corpo_secao())

        assert response.status_code == 502
        assert response.json()["type"].endswith("sugestao-ia-indisponivel")


class TestSugestaoDeExperienciaRouter:
    def test_com_contexto_de_vaga_refina_conquistas_e_contexto_e_devolve_a_descricao(
        self, client: TestClient
    ):
        perfil, adaptada = _sobrescrever_servicos_de_experiencia()
        corpo = _corpo_experiencia(contexto_vaga=CONTEXTO_VAGA)
        corpo["experiencia"]["descricao"] = "- Criei APIs.\nReduzi custos."

        response = client.post("/v1/experiencias-profissionais/sugestoes", json=corpo)

        assert response.status_code == 200
        assert response.json() == {"descricao_sugerida": "Conquista sugerida.\nContexto sugerido."}
        experiencia, contexto = adaptada.chamadas[0]
        assert experiencia == ExperienciaAdaptada(
            cargo="Dev",
            empresa="TechCorp",
            periodo="2024",
            conquistas=("Criei APIs.", "Reduzi custos."),
        )
        assert contexto.descricao_vaga == "Vaga Java com Kafka"
        assert perfil.chamadas == []

    def test_sem_contexto_de_vaga_so_melhora_a_escrita(self, client: TestClient):
        perfil, adaptada = _sobrescrever_servicos_de_experiencia()

        response = client.post(
            "/v1/experiencias-profissionais/sugestoes", json=_corpo_experiencia()
        )

        assert response.status_code == 200
        assert response.json() == {"descricao_sugerida": "Descrição sugerida."}
        assert perfil.chamadas[0].descricao == "Descrição atual."
        assert adaptada.chamadas == []

    def test_descricao_vazia_devolve_422(self, client: TestClient):
        perfil, _ = _sobrescrever_servicos_de_experiencia()
        corpo = _corpo_experiencia()
        corpo["experiencia"]["descricao"] = "  "

        response = client.post("/v1/experiencias-profissionais/sugestoes", json=corpo)

        assert response.status_code == 422
        assert perfil.chamadas == []

    def test_contexto_de_vaga_invalido_devolve_422(self, client: TestClient):
        _, adaptada = _sobrescrever_servicos_de_experiencia()
        contexto = {**CONTEXTO_VAGA, "idioma_alvo": "fr"}

        response = client.post(
            "/v1/experiencias-profissionais/sugestoes",
            json=_corpo_experiencia(contexto_vaga=contexto),
        )

        assert response.status_code == 422
        assert adaptada.chamadas == []

    def test_com_contexto_de_vaga_exige_cargo_e_empresa(self, client: TestClient):
        _, adaptada = _sobrescrever_servicos_de_experiencia()
        corpo = _corpo_experiencia(contexto_vaga=CONTEXTO_VAGA)
        corpo["experiencia"]["cargo"] = ""

        response = client.post("/v1/experiencias-profissionais/sugestoes", json=corpo)

        assert response.status_code == 422
        assert "cargo" in response.json()["detail"]
        assert adaptada.chamadas == []

    def test_ia_indisponivel_sem_contexto_devolve_502(self, client: TestClient):
        _sobrescrever_servicos_de_experiencia(perfil=ServicoExperienciaFake(erro=SugestaoIAIndisponivel()))

        response = client.post(
            "/v1/experiencias-profissionais/sugestoes", json=_corpo_experiencia()
        )

        assert response.status_code == 502

    def test_ia_indisponivel_com_contexto_devolve_502(self, client: TestClient):
        _sobrescrever_servicos_de_experiencia(
            adaptada=ServicoExperienciaAdaptadaFake(erro=SugestaoIAIndisponivel())
        )

        response = client.post(
            "/v1/experiencias-profissionais/sugestoes",
            json=_corpo_experiencia(contexto_vaga=CONTEXTO_VAGA),
        )

        assert response.status_code == 502

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.dependencies import obter_service_extrair_dados_vaga
from jobsync.entrypoints.api.main import app
from jobsync.vaga import (
    DadosVaga,
    FonteVagaNaoSuportada,
    LeituraVagaIndisponivel,
    LimiteLeituraVagaExcedido,
    LinkVagaInvalido,
    MotivoLeituraIndisponivel,
)

URL = "https://www.linkedin.com/jobs/view/4484559483/"


class ServiceFake:
    def __init__(self, dados: DadosVaga | None = None, erro: Exception | None = None):
        self.dados = dados
        self.erro = erro
        self.entradas: list = []

    def executar(self, input_dto):
        self.entradas.append(input_dto)
        if self.erro:
            raise self.erro
        return self.dados


def _dados_completos() -> DadosVaga:
    return DadosVaga(
        descricao="Descrição completa da vaga.",
        cargo="Engenheiro de Software",
        empresa="Barte",
        local="Brasil",
        url=URL,
        tipo_contratacao="Tempo integral",
        senioridade="Sênior",
        setor="Serviços financeiros",
    )


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    yield TestClient(app)
    app.dependency_overrides.pop(obter_service_extrair_dados_vaga, None)


def _usar(service: ServiceFake) -> ServiceFake:
    app.dependency_overrides[obter_service_extrair_dados_vaga] = lambda: service
    return service


class TestExtracaoVagaRouter:
    def test_extrai_dados_a_partir_do_link(self, client: TestClient, como_perfil):
        como_perfil("perfil-1")
        service = _usar(ServiceFake(dados=_dados_completos()))

        response = client.post("/v1/vagas/extracoes", json={"url": URL})

        assert response.status_code == 200
        assert response.json() == {
            "cargo": "Engenheiro de Software",
            "empresa": "Barte",
            "local": "Brasil",
            "descricao": "Descrição completa da vaga.",
            "url": URL,
            "tipo_contratacao": "Tempo integral",
            "senioridade": "Sênior",
            "setor": "Serviços financeiros",
        }
        assert service.entradas[0].url == URL
        assert service.entradas[0].texto is None
        assert service.entradas[0].usuario_id == "perfil-1"

    def test_extrai_dados_a_partir_do_texto(self, client: TestClient):
        service = _usar(ServiceFake(dados=DadosVaga(descricao="Texto da vaga")))

        response = client.post("/v1/vagas/extracoes", json={"texto": "Texto da vaga"})

        assert response.status_code == 200
        assert response.json()["descricao"] == "Texto da vaga"
        assert response.json()["cargo"] is None
        assert service.entradas[0].texto == "Texto da vaga"
        assert service.entradas[0].url is None

    def test_repassa_link_e_texto_quando_informados_juntos(self, client: TestClient):
        service = _usar(ServiceFake(dados=DadosVaga(descricao="Texto")))

        client.post("/v1/vagas/extracoes", json={"url": URL, "texto": "Texto"})

        assert service.entradas[0].url == URL
        assert service.entradas[0].texto == "Texto"

    @pytest.mark.parametrize(
        "corpo",
        [{}, {"url": None, "texto": None}, {"url": "  ", "texto": "   "}, {"texto": "a" * 50_001}, {"url": "a" * 2049}],
    )
    def test_rejeita_corpo_sem_dados_ou_acima_dos_limites(self, client: TestClient, corpo):
        service = _usar(ServiceFake(dados=DadosVaga(descricao="Texto")))

        response = client.post("/v1/vagas/extracoes", json=corpo)

        assert response.status_code == 422
        assert response.json()["title"] == "Requisição inválida"
        assert service.entradas == []

    def test_link_invalido_devolve_422_em_problem_details(self, client: TestClient):
        _usar(ServiceFake(erro=LinkVagaInvalido("O link do LinkedIn não identifica uma vaga específica.")))

        response = client.post("/v1/vagas/extracoes", json={"url": "https://www.linkedin.com/jobs/search/"})

        assert response.status_code == 422
        corpo = response.json()
        assert corpo["status"] == 422
        assert corpo["title"] == "Link da vaga inválido"
        assert corpo["type"].endswith("/link-vaga-invalido")
        assert "não identifica uma vaga" in corpo["detail"]
        assert corpo["instance"].endswith("/v1/vagas/extracoes")

    def test_fonte_nao_suportada_devolve_422(self, client: TestClient):
        _usar(ServiceFake(erro=FonteVagaNaoSuportada("A leitura de links do LinkedIn está desativada.")))

        response = client.post("/v1/vagas/extracoes", json={"url": URL})

        assert response.status_code == 422
        assert response.json()["title"] == "Fonte de vaga não suportada"
        assert response.json()["type"].endswith("/fonte-vaga-nao-suportada")
        assert "desativada" in response.json()["detail"]

    def test_limite_excedido_devolve_429_com_retry_after(self, client: TestClient):
        _usar(ServiceFake(erro=LimiteLeituraVagaExcedido(segundos_para_nova_tentativa=42)))

        response = client.post("/v1/vagas/extracoes", json={"url": URL})

        assert response.status_code == 429
        assert response.headers["Retry-After"] == "42"
        assert response.json()["type"].endswith("/limite-leitura-vaga")

    @pytest.mark.parametrize("motivo", list(MotivoLeituraIndisponivel))
    def test_leitura_indisponivel_devolve_502_com_a_orientacao_para_colar_o_texto(
        self, client: TestClient, motivo: MotivoLeituraIndisponivel
    ):
        _usar(ServiceFake(erro=LeituraVagaIndisponivel(motivo)))

        response = client.post("/v1/vagas/extracoes", json={"url": URL})

        assert response.status_code == 502
        corpo = response.json()
        assert corpo["title"] == "Leitura da vaga indisponível"
        assert corpo["type"].endswith("/leitura-vaga-indisponivel")
        assert "texto da vaga" in corpo["detail"].lower()

    @pytest.mark.sem_sessao_simulada
    def test_exige_sessao(self, client: TestClient):
        service = _usar(ServiceFake(dados=DadosVaga(descricao="Texto")))

        response = client.post("/v1/vagas/extracoes", json={"texto": "Texto"})

        assert response.status_code == 401
        assert service.entradas == []

    def test_a_rota_aparece_na_documentacao_openapi(self, client: TestClient):
        esquema = client.get("/openapi.json").json()

        operacao = esquema["paths"]["/v1/vagas/extracoes"]["post"]
        assert set(operacao["responses"]) >= {"200", "422", "429", "502"}

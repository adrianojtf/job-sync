"""Garante que toda rota de dados exige sessão e só aceita o perfil do usuário autenticado."""

from collections.abc import Generator

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_servicos_autenticacao
from jobsync.tests.entrypoints.api.apoio_autenticacao import FRONTEND, montar_mundo

pytestmark = pytest.mark.sem_sessao_simulada

ROTAS_PUBLICAS = {
    ("GET", "/v1/health"),
    ("POST", "/v1/sessoes"),
    ("POST", "/v1/sessoes/simples"),
    ("DELETE", "/v1/sessoes/atual"),
    ("POST", "/v1/usuarios"),
    ("PUT", "/v1/confirmacoes-email/{token}"),
    ("POST", "/v1/redefinicoes-senha"),
    ("PUT", "/v1/redefinicoes-senha/{token}"),
    ("GET", "/v1/provedores"),
    ("GET", "/v1/provedores/{provedor}/autorizacao"),
    ("GET", "/v1/provedores/{provedor}/retorno"),
}
PERFIL_DA_SESSAO = "meu-perfil"
PERFIL_ALHEIO = "perfil-de-outra-pessoa"


def _rotas_da_api() -> list[tuple[str, str, APIRoute]]:
    return [
        (metodo, rota.path, rota)
        for rota in app.routes
        if isinstance(rota, APIRoute) and rota.path.startswith("/v1")
        for metodo in sorted(rota.methods - {"HEAD", "OPTIONS"})
    ]


def _substituir(caminho: str) -> str:
    saida, dentro = [], False
    for caractere in caminho:
        if caractere == "{":
            dentro = True
            saida.append("x")
        elif caractere == "}":
            dentro = False
        elif not dentro:
            saida.append(caractere)
    return "".join(saida)


@pytest.fixture
def mundo():
    return montar_mundo(login_simples=True)


@pytest.fixture
def anonimo(mundo) -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_servicos_autenticacao] = lambda: mundo.servicos
    yield TestClient(app, base_url=FRONTEND, follow_redirects=False)
    app.dependency_overrides.pop(obter_servicos_autenticacao, None)


@pytest.fixture
def autenticado(anonimo) -> TestClient:
    resposta = anonimo.post("/v1/sessoes/simples", json={"identificador": PERFIL_DA_SESSAO})
    assert resposta.status_code == 201
    return anonimo


def _protegidas() -> list[tuple[str, str, APIRoute]]:
    return [(m, c, r) for m, c, r in _rotas_da_api() if (m, c) not in ROTAS_PUBLICAS]


def _com_perfil() -> list[tuple[str, str, APIRoute]]:
    return [(m, c, r) for m, c, r in _protegidas() if _parametros_de_perfil(r) or _corpo_tem_perfil(r)]


def _parametros_de_perfil(rota: APIRoute) -> set[str]:
    return {
        parametro.name
        for parametro in [*rota.dependant.path_params, *rota.dependant.query_params]
        if parametro.name == "perfil_identificador"
    }


def _corpo_tem_perfil(rota: APIRoute) -> bool:
    campo = rota.body_field
    modelo = getattr(campo, "type_", None) if campo is not None else None
    return hasattr(modelo, "model_fields") and "perfil_identificador" in modelo.model_fields


class TestTodasAsRotasExigemSessao:
    def test_o_app_tem_rotas_protegidas_para_varrer(self):
        assert len(_protegidas()) >= 25

    @pytest.mark.parametrize("metodo,caminho,rota", _protegidas(), ids=lambda v: v if isinstance(v, str) else "")
    def test_sem_sessao_responde_401(self, anonimo, metodo, caminho, rota):
        resposta = anonimo.request(metodo, _substituir(caminho))

        assert resposta.status_code == 401, f"{metodo} {caminho} aceitou requisição sem sessão"

    @pytest.mark.parametrize("metodo,caminho,rota", _protegidas(), ids=lambda v: v if isinstance(v, str) else "")
    def test_cookie_forjado_responde_401(self, anonimo, metodo, caminho, rota):
        anonimo.cookies.set("js_sessao", "forjado")

        resposta = anonimo.request(metodo, _substituir(caminho))

        assert resposta.status_code == 401, f"{metodo} {caminho} aceitou sessão forjada"


class TestSoAceitaOPerfilDaSessao:
    def test_ha_rotas_com_perfil_no_caminho_na_query_e_no_corpo(self):
        rotas = _protegidas()

        assert any(_parametros_de_perfil(r) for _, _, r in rotas)
        assert any(_corpo_tem_perfil(r) for _, _, r in rotas)
        assert len(_com_perfil()) >= 14

    @pytest.mark.parametrize("metodo,caminho,rota", _com_perfil(), ids=lambda v: v if isinstance(v, str) else "")
    def test_perfil_de_outra_pessoa_responde_403(self, autenticado, metodo, caminho, rota):
        url = _substituir(caminho)
        argumentos = {}
        if "perfil_identificador" in {p.name for p in rota.dependant.path_params}:
            url = caminho.replace("{perfil_identificador}", PERFIL_ALHEIO)
            url = _substituir_restantes(url)
        elif any(p.name == "perfil_identificador" for p in rota.dependant.query_params):
            argumentos["params"] = {"perfil_identificador": PERFIL_ALHEIO}
        if _corpo_tem_perfil(rota):
            argumentos["json"] = {"perfil_identificador": PERFIL_ALHEIO}

        resposta = autenticado.request(metodo, url, **argumentos)

        assert resposta.status_code == 403, f"{metodo} {caminho} aceitou o perfil de outra pessoa"
        assert resposta.json()["type"].endswith("/acesso-negado")


def _substituir_restantes(caminho: str) -> str:
    return _substituir(caminho) if "{" in caminho else caminho


class TestPerfilPorId:
    def test_devolve_o_proprio_perfil(self, autenticado):
        resposta = autenticado.get(f"/v1/perfis/{PERFIL_DA_SESSAO}")

        assert resposta.status_code == 200
        assert resposta.json() == {"identificador": PERFIL_DA_SESSAO}

    def test_perfil_alheio_responde_403_e_nao_cria_perfil(self, autenticado, mundo):
        resposta = autenticado.get(f"/v1/perfis/{PERFIL_ALHEIO}")

        assert resposta.status_code == 403
        assert mundo.usuarios.buscar_por_perfil(PERFIL_ALHEIO) is None

    def test_sem_sessao_nao_cria_perfil(self, anonimo, mundo):
        resposta = anonimo.get("/v1/perfis/qualquer-um")

        assert resposta.status_code == 401
        assert mundo.usuarios.buscar_por_perfil("qualquer-um") is None


class TestCandidaturaDeOutroUsuario:
    def test_mover_candidatura_de_outro_perfil_responde_404(self, autenticado):
        from datetime import datetime, timezone

        from jobsync.candidatura.adapters import CandidaturaRepositoryFake
        from jobsync.candidatura.domain.candidatura import Candidatura, StatusCandidatura
        from jobsync.entrypoints.dependencies import obter_repositorio_candidatura

        repositorio = CandidaturaRepositoryFake()
        alheia = repositorio.salvar(
            Candidatura.nova(
                PERFIL_ALHEIO, "vaga-1", "curriculo-1", "Acme", "Dev", datetime(2026, 1, 1, tzinfo=timezone.utc)
            )
        )
        app.dependency_overrides[obter_repositorio_candidatura] = lambda: repositorio
        try:
            resposta = autenticado.post(f"/v1/candidaturas/{alheia.id}/submissao", json={"novo_status": "entrevista"})
        finally:
            app.dependency_overrides.pop(obter_repositorio_candidatura, None)

        assert resposta.status_code == 404
        assert repositorio.buscar_por_id(alheia.id).status == StatusCandidatura.APLICADO

    def test_mover_a_propria_candidatura_funciona(self, autenticado):
        from datetime import datetime, timezone

        from jobsync.candidatura.adapters import CandidaturaRepositoryFake
        from jobsync.candidatura.domain.candidatura import Candidatura, StatusCandidatura
        from jobsync.entrypoints.dependencies import obter_repositorio_candidatura

        repositorio = CandidaturaRepositoryFake()
        propria = repositorio.salvar(
            Candidatura.nova(
                PERFIL_DA_SESSAO, "vaga-1", "curriculo-1", "Acme", "Dev", datetime(2026, 1, 1, tzinfo=timezone.utc)
            )
        )
        app.dependency_overrides[obter_repositorio_candidatura] = lambda: repositorio
        try:
            resposta = autenticado.post(f"/v1/candidaturas/{propria.id}/submissao", json={"novo_status": "entrevista"})
        finally:
            app.dependency_overrides.pop(obter_repositorio_candidatura, None)

        assert resposta.status_code == 200
        assert repositorio.buscar_por_id(propria.id).status == StatusCandidatura.ENTREVISTA


class TestExigirPerfilDaRequisicao:
    @pytest.fixture
    def cliente(self, mundo):
        from fastapi import Depends, FastAPI

        from jobsync.entrypoints.api.autorizacao import exigir_perfil_da_requisicao
        from jobsync.entrypoints.api.exceptions import adicionar_handlers_excecao

        mini = FastAPI()
        adicionar_handlers_excecao(mini)
        mini.dependency_overrides[obter_servicos_autenticacao] = lambda: mundo.servicos

        @mini.get("/caminho/{perfil_identificador}", dependencies=[Depends(exigir_perfil_da_requisicao)])
        def por_caminho(perfil_identificador: str) -> dict:
            return {"ok": True}

        @mini.get("/query", dependencies=[Depends(exigir_perfil_da_requisicao)])
        def por_query(perfil_identificador: str | None = None) -> dict:
            return {"ok": True}

        @mini.post("/corpo", dependencies=[Depends(exigir_perfil_da_requisicao)])
        def por_corpo(dados: dict) -> dict:
            return {"ok": True}

        cliente = TestClient(mini, base_url=FRONTEND)
        assert cliente.post("/v1/sessoes/simples", json={"identificador": PERFIL_DA_SESSAO}).status_code in (201, 404)
        return cliente

    @pytest.fixture
    def com_sessao(self, mundo, cliente):
        resultado = mundo.servicos.entrar_com_identificador_simples.executar(PERFIL_DA_SESSAO)
        cliente.cookies.set("js_sessao", resultado.token)
        return cliente

    def test_caminho_proprio_passa_e_alheio_e_negado(self, com_sessao):
        assert com_sessao.get(f"/caminho/{PERFIL_DA_SESSAO}").status_code == 200
        assert com_sessao.get(f"/caminho/{PERFIL_ALHEIO}").status_code == 403

    def test_query_propria_passa_e_alheia_e_negada(self, com_sessao):
        assert com_sessao.get("/query", params={"perfil_identificador": PERFIL_DA_SESSAO}).status_code == 200
        assert com_sessao.get("/query", params={"perfil_identificador": PERFIL_ALHEIO}).status_code == 403

    def test_query_com_valor_repetido_nega_se_algum_for_alheio(self, com_sessao):
        resposta = com_sessao.get(f"/query?perfil_identificador={PERFIL_DA_SESSAO}&perfil_identificador={PERFIL_ALHEIO}")

        assert resposta.status_code == 403

    def test_corpo_proprio_passa_e_alheio_e_negado(self, com_sessao):
        assert com_sessao.post("/corpo", json={"perfil_identificador": PERFIL_DA_SESSAO}).status_code == 200
        assert com_sessao.post("/corpo", json={"perfil_identificador": PERFIL_ALHEIO}).status_code == 403

    def test_corpo_com_perfil_numerico_nao_burla_a_checagem(self, com_sessao):
        assert com_sessao.post("/corpo", json={"perfil_identificador": 123}).status_code == 403

    def test_requisicao_sem_perfil_informado_passa_com_sessao(self, com_sessao):
        assert com_sessao.get("/query").status_code == 200
        assert com_sessao.post("/corpo", json={"outro": 1}).status_code == 200

    def test_corpo_que_nao_e_json_e_ignorado(self, com_sessao):
        resposta = com_sessao.post("/corpo", content=b"texto", headers={"content-type": "text/plain"})

        assert resposta.status_code != 403

    def test_sem_sessao_responde_401(self, cliente):
        assert cliente.get("/query").status_code == 401

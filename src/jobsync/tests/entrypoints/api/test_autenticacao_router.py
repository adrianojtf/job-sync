"""Testes de API dos fluxos de autenticação (serviços reais sobre repositórios fake)."""

from collections.abc import Generator
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

from jobsync.autenticacao.domain.exceptions import EnvioEmailFalhou, ProvedorIndisponivel
from jobsync.autenticacao.domain.provedor_identidade import IdentidadeAutenticada
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import obter_servicos_autenticacao
from jobsync.tests.entrypoints.api.apoio_autenticacao import FRONTEND, montar_mundo

SENHA = "uma-senha-longa-1"

pytestmark = pytest.mark.sem_sessao_simulada


@pytest.fixture
def mundo():
    return montar_mundo()


@pytest.fixture
def client(mundo) -> Generator[TestClient, None, None]:
    app.dependency_overrides[obter_servicos_autenticacao] = lambda: mundo.servicos
    yield TestClient(app, base_url=FRONTEND, follow_redirects=False)
    app.dependency_overrides.pop(obter_servicos_autenticacao, None)


def _cadastrar_e_confirmar(client, mundo, email="ana@exemplo.com", senha=SENHA):
    assert client.post("/v1/usuarios", json={"email": email, "senha": senha}).status_code == 202
    token = mundo.enviador.ultimo_token(email)
    assert client.put(f"/v1/confirmacoes-email/{token}").status_code == 204


def _entrar(client, email="ana@exemplo.com", senha=SENHA):
    return client.post("/v1/sessoes", json={"email": email, "senha": senha})


class TestCadastroEConfirmacao:
    def test_cadastro_responde_202_e_envia_confirmacao(self, client, mundo):
        resposta = client.post("/v1/usuarios", json={"email": "ana@exemplo.com", "senha": SENHA})

        assert resposta.status_code == 202
        assert mundo.enviador.ultimo_token("ana@exemplo.com")

    def test_cadastro_de_email_ja_confirmado_tem_a_mesma_resposta(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)

        resposta = client.post("/v1/usuarios", json={"email": "ana@exemplo.com", "senha": SENHA})
        novo = client.post("/v1/usuarios", json={"email": "bia@exemplo.com", "senha": SENHA})

        assert resposta.status_code == novo.status_code == 202
        assert resposta.json() == novo.json()

    @pytest.mark.parametrize(
        "corpo",
        [
            {"email": "invalido", "senha": SENHA},
            {"email": "ana@exemplo.com", "senha": "curta"},
            {"email": "ana@exemplo.com", "senha": "1234567890"},
            {"email": "ana@exemplo.com"},
        ],
    )
    def test_dados_invalidos_geram_422_em_formato_problem(self, client, corpo):
        resposta = client.post("/v1/usuarios", json=corpo)

        assert resposta.status_code == 422
        assert resposta.json()["status"] == 422

    def test_confirmacao_com_link_invalido_gera_400(self, client):
        resposta = client.put("/v1/confirmacoes-email/nao-existe")

        assert resposta.status_code == 400
        assert resposta.json()["type"].endswith("/token-invalido")

    def test_falha_no_envio_do_email_gera_503(self, client, mundo):
        def quebrar(para, assunto, corpo):
            raise EnvioEmailFalhou("smtp fora do ar")

        mundo.enviador.enviar = quebrar

        resposta = client.post("/v1/usuarios", json={"email": "ana@exemplo.com", "senha": SENHA})

        assert resposta.status_code == 503


class TestLoginComSenha:
    def test_login_cria_sessao_com_cookie_httponly(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)

        resposta = _entrar(client)

        cookie = resposta.headers["set-cookie"].lower()
        assert resposta.status_code == 201
        assert resposta.headers["location"] == "/v1/sessoes/atual"
        assert "js_sessao=" in cookie
        assert "httponly" in cookie
        assert "samesite=lax" in cookie
        assert "path=/" in cookie
        assert "secure" not in cookie
        assert "max-age=2592000" in cookie

    def test_cookie_secure_quando_configurado(self, mundo):
        mundo = montar_mundo(cookie_secure=True)
        app.dependency_overrides[obter_servicos_autenticacao] = lambda: mundo.servicos
        try:
            cliente = TestClient(app, base_url=FRONTEND, follow_redirects=False)
            cliente.post("/v1/usuarios", json={"email": "ana@exemplo.com", "senha": SENHA})
            cliente.put(f"/v1/confirmacoes-email/{mundo.enviador.ultimo_token('ana@exemplo.com')}")

            resposta = cliente.post("/v1/sessoes", json={"email": "ana@exemplo.com", "senha": SENHA})
        finally:
            app.dependency_overrides.pop(obter_servicos_autenticacao, None)

        assert "secure" in resposta.headers["set-cookie"].lower()

    def test_resposta_traz_o_usuario_e_o_perfil(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)

        corpo = _entrar(client).json()

        assert corpo["email"] == "ana@exemplo.com"
        assert corpo["perfil_identificador"].startswith("u-")
        assert "senha" not in corpo

    def test_credenciais_erradas_geram_401_sem_cookie(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)

        resposta = _entrar(client, senha="senha-errada-123")

        assert resposta.status_code == 401
        assert "set-cookie" not in resposta.headers
        assert resposta.json()["detail"] == "E-mail ou senha incorretos."

    def test_email_desconhecido_tem_a_mesma_resposta(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)

        conhecido = _entrar(client, senha="senha-errada-123")
        desconhecido = _entrar(client, email="ninguem@exemplo.com")

        assert (desconhecido.status_code, desconhecido.json()["detail"]) == (
            conhecido.status_code,
            conhecido.json()["detail"],
        )

    def test_conta_nao_confirmada_nao_entra(self, client, mundo):
        client.post("/v1/usuarios", json={"email": "ana@exemplo.com", "senha": SENHA})

        assert _entrar(client).status_code == 401

    def test_excesso_de_falhas_gera_429_com_retry_after(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)
        for _ in range(5):
            _entrar(client, senha="senha-errada-123")

        resposta = _entrar(client)

        assert resposta.status_code == 429
        assert resposta.headers["retry-after"] == str(15 * 60)


class TestSessao:
    def test_usuarios_me_devolve_o_usuario_da_sessao(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)
        _entrar(client)

        resposta = client.get("/v1/usuarios/me")

        assert resposta.status_code == 200
        assert resposta.json()["email"] == "ana@exemplo.com"

    def test_usuarios_me_sem_sessao_gera_401(self, client):
        resposta = client.get("/v1/usuarios/me")

        assert resposta.status_code == 401
        assert resposta.json()["type"].endswith("/nao-autenticado")

    def test_usuarios_me_com_cookie_forjado_gera_401(self, client):
        client.cookies.set("js_sessao", "forjado")

        assert client.get("/v1/usuarios/me").status_code == 401

    def test_logout_encerra_a_sessao_e_limpa_o_cookie(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)
        _entrar(client)

        resposta = client.delete("/v1/sessoes/atual")

        assert resposta.status_code == 204
        assert "js_sessao=" in resposta.headers["set-cookie"]
        assert "max-age=0" in resposta.headers["set-cookie"].lower()
        assert client.get("/v1/usuarios/me").status_code == 401

    def test_logout_sem_sessao_tambem_responde_204(self, client):
        assert client.delete("/v1/sessoes/atual").status_code == 204

    def test_sessao_expira_por_inatividade(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)
        _entrar(client)
        mundo.relogio.avancar(days=8)

        assert client.get("/v1/usuarios/me").status_code == 401


class TestRedefinicaoDeSenha:
    def test_pedido_tem_a_mesma_resposta_para_email_conhecido_e_desconhecido(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)

        conhecido = client.post("/v1/redefinicoes-senha", json={"email": "ana@exemplo.com"})
        desconhecido = client.post("/v1/redefinicoes-senha", json={"email": "ninguem@exemplo.com"})

        assert conhecido.status_code == desconhecido.status_code == 202
        assert conhecido.json() == desconhecido.json()
        assert mundo.enviador.para("ninguem@exemplo.com") == []

    def test_fluxo_completo_troca_a_senha_e_derruba_sessoes(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)
        _entrar(client)
        client.post("/v1/redefinicoes-senha", json={"email": "ana@exemplo.com"})
        token = mundo.enviador.ultimo_token("ana@exemplo.com")

        resposta = client.put(f"/v1/redefinicoes-senha/{token}", json={"nova_senha": "nova-senha-longa-9"})

        assert resposta.status_code == 204
        assert client.get("/v1/usuarios/me").status_code == 401
        assert _entrar(client, senha=SENHA).status_code == 401
        assert _entrar(client, senha="nova-senha-longa-9").status_code == 201

    def test_senha_fraca_gera_422(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)
        client.post("/v1/redefinicoes-senha", json={"email": "ana@exemplo.com"})
        token = mundo.enviador.ultimo_token("ana@exemplo.com")

        assert client.put(f"/v1/redefinicoes-senha/{token}", json={"nova_senha": "curta"}).status_code == 422

    def test_link_invalido_gera_400(self, client):
        resposta = client.put("/v1/redefinicoes-senha/nao-existe", json={"nova_senha": "nova-senha-longa-9"})

        assert resposta.status_code == 400


class TestProvedores:
    def test_lista_os_metodos_disponiveis(self, client):
        corpo = client.get("/v1/provedores").json()

        assert corpo == {"provedores": ["google"], "senha": True, "login_simples": False}

    def test_login_simples_aparece_quando_habilitado(self):
        mundo = montar_mundo(login_simples=True)
        app.dependency_overrides[obter_servicos_autenticacao] = lambda: mundo.servicos
        try:
            corpo = TestClient(app).get("/v1/provedores").json()
        finally:
            app.dependency_overrides.pop(obter_servicos_autenticacao, None)

        assert corpo["login_simples"] is True


class TestLoginSimples:
    def test_desabilitado_responde_404(self, client):
        assert client.post("/v1/sessoes/simples", json={"identificador": "matheus"}).status_code == 404

    def test_habilitado_cria_sessao_no_perfil_do_identificador(self):
        mundo = montar_mundo(login_simples=True)
        app.dependency_overrides[obter_servicos_autenticacao] = lambda: mundo.servicos
        try:
            cliente = TestClient(app, base_url=FRONTEND)

            resposta = cliente.post("/v1/sessoes/simples", json={"identificador": "matheus"})
            me = cliente.get("/v1/usuarios/me")
        finally:
            app.dependency_overrides.pop(obter_servicos_autenticacao, None)

        assert resposta.status_code == 201
        assert resposta.json()["perfil_identificador"] == "matheus"
        assert me.json()["perfil_identificador"] == "matheus"

    def test_identificador_vazio_gera_422(self):
        mundo = montar_mundo(login_simples=True)
        app.dependency_overrides[obter_servicos_autenticacao] = lambda: mundo.servicos
        try:
            resposta = TestClient(app).post("/v1/sessoes/simples", json={"identificador": "  "})
        finally:
            app.dependency_overrides.pop(obter_servicos_autenticacao, None)

        assert resposta.status_code == 422


def _iniciar_google(client, destino="/vagas"):
    resposta = client.get("/v1/provedores/google/autorizacao", params={"destino": destino})
    estado = parse_qs(urlparse(resposta.headers["location"]).query)["state"][0]
    return resposta, estado


class TestLoginGoogle:
    def test_autorizacao_redireciona_ao_provedor_e_define_cookie_de_estado(self, client):
        resposta, estado = _iniciar_google(client)

        assert resposta.status_code == 302
        assert resposta.headers["location"].startswith("https://idp.teste/auth?")
        cookie = resposta.headers["set-cookie"].lower()
        assert f"js_oauth={estado}".lower() in cookie
        assert "httponly" in cookie
        assert "path=/v1/provedores" in cookie
        assert "samesite=lax" in cookie

    def test_autorizacao_de_provedor_desconhecido_gera_404(self, client):
        assert client.get("/v1/provedores/facebook/autorizacao").status_code == 404

    def test_retorno_cria_sessao_e_leva_ao_destino(self, client):
        _, estado = _iniciar_google(client, "/candidaturas")

        resposta = client.get("/v1/provedores/google/retorno", params={"code": "c", "state": estado})

        assert resposta.status_code == 302
        assert resposta.headers["location"] == f"{FRONTEND}/candidaturas"
        assert any("js_sessao=" in c for c in resposta.headers.get_list("set-cookie"))
        assert client.get("/v1/usuarios/me").json()["email"] == "ana@exemplo.com"

    def test_retorno_remove_o_cookie_de_estado(self, client):
        _, estado = _iniciar_google(client)

        resposta = client.get("/v1/provedores/google/retorno", params={"code": "c", "state": estado})

        apagado = [c for c in resposta.headers.get_list("set-cookie") if c.startswith("js_oauth=")]
        assert apagado and "max-age=0" in apagado[0].lower()

    def test_destino_externo_e_ignorado(self, client):
        _, estado = _iniciar_google(client, "https://evil.example.com")

        resposta = client.get("/v1/provedores/google/retorno", params={"code": "c", "state": estado})

        assert resposta.headers["location"] == f"{FRONTEND}/"

    def test_usuario_cancelou_no_google(self, client):
        resposta = client.get("/v1/provedores/google/retorno", params={"error": "access_denied"})

        assert resposta.status_code == 302
        assert resposta.headers["location"] == f"{FRONTEND}/entrar?erro=acesso_negado"

    @pytest.mark.parametrize("parametros", [{}, {"code": "c"}, {"state": "x"}, {"code": "c", "state": "forjado"}])
    def test_retorno_sem_estado_valido(self, client, parametros):
        resposta = client.get("/v1/provedores/google/retorno", params=parametros)

        assert resposta.headers["location"] == f"{FRONTEND}/entrar?erro=estado_invalido"
        assert not any("js_sessao=" in c for c in resposta.headers.get_list("set-cookie"))

    def test_estado_sem_o_cookie_do_navegador_e_recusado(self, client, mundo):
        _, estado = _iniciar_google(client)
        client.cookies.clear()

        resposta = client.get("/v1/provedores/google/retorno", params={"code": "c", "state": estado})

        assert resposta.headers["location"] == f"{FRONTEND}/entrar?erro=estado_invalido"

    def test_email_nao_verificado(self, client, mundo):
        mundo.provedor.identidade = IdentidadeAutenticada("google", "sub-1", "ana@exemplo.com", False, None)
        _, estado = _iniciar_google(client)

        resposta = client.get("/v1/provedores/google/retorno", params={"code": "c", "state": estado})

        assert resposta.headers["location"] == f"{FRONTEND}/entrar?erro=email_nao_verificado"

    def test_provedor_indisponivel(self, client, mundo):
        mundo.provedor.erro = ProvedorIndisponivel("fora")
        _, estado = _iniciar_google(client)

        resposta = client.get("/v1/provedores/google/retorno", params={"code": "c", "state": estado})

        assert resposta.headers["location"] == f"{FRONTEND}/entrar?erro=provedor_indisponivel"

    def test_retorno_de_provedor_desconhecido_gera_404(self, client):
        assert client.get("/v1/provedores/facebook/retorno", params={"code": "c", "state": "x"}).status_code == 404

    def test_google_e_senha_levam_ao_mesmo_perfil(self, client, mundo):
        _cadastrar_e_confirmar(client, mundo)
        perfil_senha = _entrar(client).json()["perfil_identificador"]
        client.delete("/v1/sessoes/atual")
        _, estado = _iniciar_google(client)

        client.get("/v1/provedores/google/retorno", params={"code": "c", "state": estado})

        assert client.get("/v1/usuarios/me").json()["perfil_identificador"] == perfil_senha

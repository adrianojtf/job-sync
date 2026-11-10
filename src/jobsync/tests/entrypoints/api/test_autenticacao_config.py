"""Testes da leitura da configuração de autenticação a partir do ambiente."""

from datetime import timedelta

import pytest

from jobsync.entrypoints.autenticacao_config import (
    configuracao_autenticacao_do_ambiente,
    configuracao_http_do_ambiente,
)


class TestConfiguracaoAutenticacaoDoAmbiente:
    def test_sem_variaveis_usa_os_padroes_da_tech_spec(self):
        config = configuracao_autenticacao_do_ambiente({})

        assert config.url_frontend == "http://localhost:8080"
        assert config.sessao_inatividade == timedelta(days=7)
        assert config.sessao_maxima == timedelta(days=30)

    def test_le_prazos_e_url(self):
        config = configuracao_autenticacao_do_ambiente(
            {
                "AUTH_BASE_URL_FRONTEND": "https://app.exemplo.com/",
                "AUTH_SESSAO_INATIVIDADE_DIAS": "2",
                "AUTH_SESSAO_MAXIMA_DIAS": "10",
            }
        )

        assert config.url_frontend == "https://app.exemplo.com/"
        assert config.sessao_inatividade == timedelta(days=2)
        assert config.sessao_maxima == timedelta(days=10)

    @pytest.mark.parametrize("valor", ["abc", "0", "-3", ""])
    def test_prazo_invalido_cai_no_padrao(self, valor):
        config = configuracao_autenticacao_do_ambiente({"AUTH_SESSAO_MAXIMA_DIAS": valor})

        assert config.sessao_maxima == timedelta(days=30)

    def test_inatividade_nunca_passa_do_limite_absoluto(self):
        config = configuracao_autenticacao_do_ambiente(
            {"AUTH_SESSAO_INATIVIDADE_DIAS": "40", "AUTH_SESSAO_MAXIMA_DIAS": "10"}
        )

        assert config.sessao_inatividade == timedelta(days=10)


class TestConfiguracaoHttpDoAmbiente:
    def test_padroes_seguros(self):
        http = configuracao_http_do_ambiente({})

        assert http.cookie_secure is False
        assert http.login_simples_habilitado is False
        assert http.nome_cookie_sessao == "js_sessao"
        assert http.cabecalho_ip_cliente is None

    def test_le_o_cabecalho_do_ip_do_cliente(self):
        http = configuracao_http_do_ambiente({"AUTH_CABECALHO_IP_CLIENTE": " X-Forwarded-For "})

        assert http.cabecalho_ip_cliente == "X-Forwarded-For"

    def test_cabecalho_do_ip_em_branco_equivale_a_ausente(self):
        assert configuracao_http_do_ambiente({"AUTH_CABECALHO_IP_CLIENTE": "  "}).cabecalho_ip_cliente is None

    @pytest.mark.parametrize("valor", ["true", "TRUE", "1", "yes"])
    def test_flags_verdadeiras(self, valor):
        http = configuracao_http_do_ambiente(
            {"AUTH_COOKIE_SECURE": valor, "AUTH_LOGIN_SIMPLES_HABILITADO": valor}
        )

        assert http.cookie_secure is True
        assert http.login_simples_habilitado is True

    @pytest.mark.parametrize("valor", ["false", "0", "", "talvez"])
    def test_flags_falsas(self, valor):
        http = configuracao_http_do_ambiente(
            {"AUTH_COOKIE_SECURE": valor, "AUTH_LOGIN_SIMPLES_HABILITADO": valor}
        )

        assert http.cookie_secure is False
        assert http.login_simples_habilitado is False

    def test_origens_permitidas_incluem_o_frontend_e_cors_explicito(self):
        http = configuracao_http_do_ambiente(
            {
                "AUTH_BASE_URL_FRONTEND": "https://app.exemplo.com/caminho",
                "CORS_ORIGINS": "http://localhost:5173, https://outro.exemplo.com",
            }
        )

        assert http.origens_permitidas == (
            "https://app.exemplo.com",
            "http://localhost:5173",
            "https://outro.exemplo.com",
        )

    def test_curinga_do_cors_nao_vira_origem_permitida(self):
        http = configuracao_http_do_ambiente({"CORS_ORIGINS": "*"})

        assert "*" not in http.origens_permitidas

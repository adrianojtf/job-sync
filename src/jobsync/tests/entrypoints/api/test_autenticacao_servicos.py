"""Testes da composição dos serviços de autenticação a partir do ambiente."""

from jobsync.autenticacao.adapters import EnviadorEmailLog, EnviadorEmailSmtp, ProvedorGoogle
from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.entrypoints.autenticacao_servicos import (
    enviador_email_do_ambiente,
    provedores_do_ambiente,
    servicos_autenticacao_do_ambiente,
)

CONFIG = ConfiguracaoAutenticacao(url_frontend="http://localhost:8080/")


class TestProvedoresDoAmbiente:
    def test_sem_credenciais_nao_registra_o_google(self):
        assert provedores_do_ambiente({}, CONFIG) == {}

    def test_credenciais_incompletas_nao_registram_o_google(self):
        assert provedores_do_ambiente({"GOOGLE_CLIENT_ID": "id"}, CONFIG) == {}

    def test_registra_o_google_com_redirecionamento_no_frontend_por_padrao(self):
        provedores = provedores_do_ambiente({"GOOGLE_CLIENT_ID": "id", "GOOGLE_CLIENT_SECRET": "segredo"}, CONFIG)

        assert isinstance(provedores["google"], ProvedorGoogle)
        assert "redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fv1%2Fprovedores%2Fgoogle%2Fretorno" in (
            provedores["google"].url_autorizacao("s", "n", "c")
        )

    def test_base_de_redirecionamento_configuravel(self):
        provedores = provedores_do_ambiente(
            {
                "GOOGLE_CLIENT_ID": "id",
                "GOOGLE_CLIENT_SECRET": "segredo",
                "AUTH_REDIRECT_BASE_URL": "http://localhost:8000",
            },
            CONFIG,
        )

        assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fv1%2Fprovedores%2Fgoogle%2Fretorno" in (
            provedores["google"].url_autorizacao("s", "n", "c")
        )


class TestEnviadorEmailDoAmbiente:
    def test_sem_smtp_usa_o_log(self):
        assert isinstance(enviador_email_do_ambiente({}), EnviadorEmailLog)

    def test_com_smtp_usa_o_adapter_smtp(self):
        assert isinstance(enviador_email_do_ambiente({"SMTP_HOST": "smtp.exemplo.com"}), EnviadorEmailSmtp)


class TestServicosAutenticacaoDoAmbiente:
    def test_monta_os_servicos_com_a_configuracao_do_ambiente(self):
        servicos = servicos_autenticacao_do_ambiente(
            object(),
            {"GOOGLE_CLIENT_ID": "id", "GOOGLE_CLIENT_SECRET": "segredo", "AUTH_LOGIN_SIMPLES_HABILITADO": "true"},
        )

        assert sorted(servicos.provedores) == ["google"]
        assert servicos.http.login_simples_habilitado is True

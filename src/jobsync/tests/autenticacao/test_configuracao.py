"""Testes da ConfiguracaoAutenticacao."""

from datetime import timedelta

from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao


class TestConfiguracaoAutenticacao:
    def test_padroes_seguem_a_tech_spec(self):
        config = ConfiguracaoAutenticacao()

        assert config.sessao_inatividade == timedelta(days=7)
        assert config.sessao_maxima == timedelta(days=30)
        assert config.validade_confirmacao_email == timedelta(hours=24)
        assert config.validade_redefinicao_senha == timedelta(hours=1)
        assert config.politica_limite.max_falhas == 5
        assert config.politica_limite_ip.max_falhas == 30

    def test_monta_link_com_parametros(self):
        config = ConfiguracaoAutenticacao(url_frontend="http://localhost:8080/")

        assert config.link_do_frontend("/confirmar-email", token="abc") == "http://localhost:8080/confirmar-email?token=abc"

    def test_monta_link_sem_parametros(self):
        assert ConfiguracaoAutenticacao().link_do_frontend("/entrar") == "http://localhost:8080/entrar"

"""Testes da entidade LimiteTentativa e da política de limite de tentativas."""

from datetime import datetime, timedelta, timezone

from jobsync.autenticacao.domain.limite_tentativa import LimiteTentativa, PoliticaLimiteTentativas

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
POLITICA = PoliticaLimiteTentativas(max_falhas=3, janela=timedelta(minutes=15), bloqueio=timedelta(minutes=10))


def _limite() -> LimiteTentativa:
    return LimiteTentativa.inicial("email:abc", AGORA)


class TestLimiteTentativa:
    def test_inicial_nao_esta_bloqueado(self):
        assert _limite().bloqueado(AGORA) is False

    def test_registrar_falha_incrementa_a_contagem(self):
        limite = _limite().registrar_falha(AGORA, POLITICA)

        assert limite.contagem == 1
        assert limite.bloqueado(AGORA) is False

    def test_bloqueia_ao_atingir_o_maximo_de_falhas(self):
        limite = _limite()

        for minutos in range(3):
            limite = limite.registrar_falha(AGORA + timedelta(minutes=minutos), POLITICA)

        assert limite.bloqueado(AGORA + timedelta(minutes=2)) is True
        assert limite.bloqueado_ate == AGORA + timedelta(minutes=2) + timedelta(minutes=10)

    def test_desbloqueia_depois_do_periodo_de_bloqueio(self):
        limite = _limite()
        for _ in range(3):
            limite = limite.registrar_falha(AGORA, POLITICA)

        assert limite.bloqueado(AGORA + timedelta(minutes=10)) is False

    def test_falha_durante_o_bloqueio_nao_altera_o_estado(self):
        limite = _limite()
        for _ in range(3):
            limite = limite.registrar_falha(AGORA, POLITICA)

        depois = limite.registrar_falha(AGORA + timedelta(minutes=1), POLITICA)

        assert depois == limite

    def test_reinicia_a_contagem_quando_a_janela_expira(self):
        limite = _limite().registrar_falha(AGORA, POLITICA).registrar_falha(AGORA, POLITICA)

        depois = limite.registrar_falha(AGORA + timedelta(minutes=15), POLITICA)

        assert depois.contagem == 1
        assert depois.janela_inicia_em == AGORA + timedelta(minutes=15)

    def test_nao_bloqueia_com_falhas_espalhadas_em_janelas_diferentes(self):
        limite = _limite()

        for janela in range(5):
            limite = limite.registrar_falha(AGORA + timedelta(minutes=20 * janela), POLITICA)

        assert limite.bloqueado(AGORA + timedelta(minutes=80)) is False

"""Testes da entidade Sessao."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from jobsync.autenticacao.domain.sessao import Sessao

INICIO = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
INATIVIDADE = timedelta(days=7)
MAXIMA = timedelta(days=30)


def _sessao() -> Sessao:
    return Sessao.iniciar(b"hash", uuid4(), INICIO, MAXIMA)


class TestSessao:
    def test_iniciar_define_expiracao_absoluta(self):
        sessao = _sessao()

        assert sessao.criada_em == INICIO
        assert sessao.ultimo_acesso_em == INICIO
        assert sessao.expira_em == INICIO + MAXIMA

    def test_nao_expira_dentro_dos_limites(self):
        sessao = _sessao()

        assert sessao.expirada(INICIO + timedelta(days=6), INATIVIDADE) is False

    def test_expira_por_inatividade(self):
        sessao = _sessao()

        assert sessao.expirada(INICIO + INATIVIDADE, INATIVIDADE) is True

    def test_renovar_adia_o_limite_de_inatividade(self):
        sessao = _sessao().renovar(INICIO + timedelta(days=6))

        assert sessao.expirada(INICIO + timedelta(days=12), INATIVIDADE) is False
        assert sessao.ultimo_acesso_em == INICIO + timedelta(days=6)

    def test_expira_no_limite_absoluto_mesmo_com_atividade(self):
        sessao = _sessao().renovar(INICIO + timedelta(days=29))

        assert sessao.expirada(INICIO + MAXIMA, INATIVIDADE) is True

    def test_renovar_nao_altera_expiracao_absoluta(self):
        sessao = _sessao().renovar(INICIO + timedelta(days=3))

        assert sessao.expira_em == INICIO + MAXIMA

    def test_expiracao_anterior_a_criacao_gera_erro(self):
        with pytest.raises(ValueError):
            Sessao(b"hash", uuid4(), INICIO, INICIO, INICIO - timedelta(seconds=1))

    def test_instantes_sem_fuso_geram_erro(self):
        with pytest.raises(ValueError):
            Sessao.iniciar(b"hash", uuid4(), datetime(2026, 1, 10, 12, 0), MAXIMA)

    def test_token_hash_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            Sessao.iniciar(b"", uuid4(), INICIO, MAXIMA)

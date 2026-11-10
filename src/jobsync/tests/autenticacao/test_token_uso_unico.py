"""Testes da entidade TokenUsoUnico."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from jobsync.autenticacao.domain.token_uso_unico import Finalidade, TokenUsoUnico

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)


def _token(validade: timedelta = timedelta(hours=1)) -> TokenUsoUnico:
    return TokenUsoUnico.emitir(b"hash", uuid4(), Finalidade.REDEFINICAO_SENHA, AGORA, validade)


class TestTokenUsoUnico:
    def test_emitir_define_validade_e_nao_usado(self):
        token = _token()

        assert token.expira_em == AGORA + timedelta(hours=1)
        assert token.usado_em is None
        assert token.finalidade is Finalidade.REDEFINICAO_SENHA

    def test_utilizavel_antes_de_expirar(self):
        assert _token().utilizavel(AGORA + timedelta(minutes=59)) is True

    def test_nao_utilizavel_depois_de_expirar(self):
        assert _token().utilizavel(AGORA + timedelta(hours=1)) is False

    def test_marcar_usado_torna_o_token_inutilizavel(self):
        usado = _token().marcar_usado(AGORA + timedelta(minutes=5))

        assert usado.usado_em == AGORA + timedelta(minutes=5)
        assert usado.utilizavel(AGORA + timedelta(minutes=6)) is False

    def test_marcar_usado_preserva_o_original(self):
        original = _token()

        original.marcar_usado(AGORA)

        assert original.usado_em is None

    def test_validade_nao_positiva_gera_erro(self):
        with pytest.raises(ValueError):
            _token(timedelta(0))

    def test_hash_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            TokenUsoUnico.emitir(b"", uuid4(), Finalidade.CONFIRMACAO_EMAIL, AGORA, timedelta(hours=1))

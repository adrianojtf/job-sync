"""Testes de contrato do TokenUsoUnicoRepository (fake e PostgreSQL)."""

from datetime import datetime, timedelta, timezone

from jobsync.autenticacao.domain.token_uso_unico import Finalidade, TokenUsoUnico

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)


def _token(usuario, finalidade=Finalidade.REDEFINICAO_SENHA, token_hash=b"tok-1") -> TokenUsoUnico:
    return TokenUsoUnico.emitir(token_hash, usuario.id, finalidade, AGORA, timedelta(hours=1))


class TestTokenUsoUnicoRepository:
    def test_consumir_devolve_o_token_marcado_como_usado(self, repositorios, usuario):
        repositorios.tokens.salvar(_token(usuario))

        consumido = repositorios.tokens.consumir(b"tok-1", Finalidade.REDEFINICAO_SENHA, AGORA)

        assert consumido.usuario_id == usuario.id
        assert consumido.usado_em == AGORA

    def test_token_so_pode_ser_consumido_uma_vez(self, repositorios, usuario):
        repositorios.tokens.salvar(_token(usuario))
        repositorios.tokens.consumir(b"tok-1", Finalidade.REDEFINICAO_SENHA, AGORA)

        assert repositorios.tokens.consumir(b"tok-1", Finalidade.REDEFINICAO_SENHA, AGORA) is None

    def test_token_expirado_nao_e_consumido(self, repositorios, usuario):
        repositorios.tokens.salvar(_token(usuario))

        depois = AGORA + timedelta(hours=1)

        assert repositorios.tokens.consumir(b"tok-1", Finalidade.REDEFINICAO_SENHA, depois) is None

    def test_finalidade_diferente_nao_consome(self, repositorios, usuario):
        repositorios.tokens.salvar(_token(usuario))

        assert repositorios.tokens.consumir(b"tok-1", Finalidade.CONFIRMACAO_EMAIL, AGORA) is None

    def test_token_inexistente_devolve_none(self, repositorios):
        assert repositorios.tokens.consumir(b"nada", Finalidade.CONFIRMACAO_EMAIL, AGORA) is None

    def test_remover_do_usuario_invalida_tokens_da_finalidade(self, repositorios, usuario):
        repositorios.tokens.salvar(_token(usuario, Finalidade.REDEFINICAO_SENHA, b"reset"))
        repositorios.tokens.salvar(_token(usuario, Finalidade.CONFIRMACAO_EMAIL, b"confirma"))

        repositorios.tokens.remover_do_usuario(usuario.id, Finalidade.REDEFINICAO_SENHA)

        assert repositorios.tokens.consumir(b"reset", Finalidade.REDEFINICAO_SENHA, AGORA) is None
        assert repositorios.tokens.consumir(b"confirma", Finalidade.CONFIRMACAO_EMAIL, AGORA) is not None

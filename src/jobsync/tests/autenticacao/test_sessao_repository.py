"""Testes de contrato do SessaoRepository (fake e PostgreSQL)."""

from datetime import datetime, timedelta, timezone

from jobsync.autenticacao.domain.sessao import Sessao

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)


def _sessao(usuario, token_hash=b"sessao-1") -> Sessao:
    return Sessao.iniciar(token_hash, usuario.id, AGORA, timedelta(days=30))


class TestSessaoRepository:
    def test_buscar_devolve_a_sessao_salva(self, repositorios, usuario):
        sessao = _sessao(usuario)
        repositorios.sessoes.salvar(sessao)

        assert repositorios.sessoes.buscar(b"sessao-1") == sessao

    def test_buscar_inexistente_devolve_none(self, repositorios):
        assert repositorios.sessoes.buscar(b"nada") is None

    def test_atualizar_persiste_o_ultimo_acesso(self, repositorios, usuario):
        sessao = _sessao(usuario)
        repositorios.sessoes.salvar(sessao)

        repositorios.sessoes.atualizar(sessao.renovar(AGORA + timedelta(hours=2)))

        assert repositorios.sessoes.buscar(b"sessao-1").ultimo_acesso_em == AGORA + timedelta(hours=2)

    def test_remover_apaga_somente_a_sessao_indicada(self, repositorios, usuario):
        repositorios.sessoes.salvar(_sessao(usuario, b"a"))
        repositorios.sessoes.salvar(_sessao(usuario, b"b"))

        repositorios.sessoes.remover(b"a")

        assert repositorios.sessoes.buscar(b"a") is None
        assert repositorios.sessoes.buscar(b"b") is not None

    def test_remover_todas_do_usuario(self, repositorios, usuario):
        repositorios.sessoes.salvar(_sessao(usuario, b"a"))
        repositorios.sessoes.salvar(_sessao(usuario, b"b"))

        repositorios.sessoes.remover_todas_do_usuario(usuario.id)

        assert repositorios.sessoes.buscar(b"a") is None
        assert repositorios.sessoes.buscar(b"b") is None

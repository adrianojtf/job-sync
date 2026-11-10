"""Testes de integração da migração 0003_autenticacao."""

from uuid import uuid4

import psycopg
import pytest

_TABELAS = (
    "usuario",
    "identidade_externa",
    "credencial_senha",
    "sessao",
    "token_uso_unico",
    "estado_oauth",
    "limite_tentativa",
)


def _criar_usuario(conexao, email="a@b.com", perfil="u-aaaaaaaaaaaa"):
    usuario_id = uuid4()
    conexao.execute("INSERT INTO perfil (identificador) VALUES (%s) ON CONFLICT DO NOTHING", (perfil,))
    conexao.execute(
        "INSERT INTO usuario (id, email, perfil_identificador) VALUES (%s, %s, %s)",
        (usuario_id, email, perfil),
    )
    return usuario_id


class TestMigracaoAutenticacao:
    def test_cria_todas_as_tabelas(self, pool_postgres):
        with pool_postgres.connection() as conexao:
            existentes = {
                linha[0]
                for linha in conexao.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                ).fetchall()
            }

        assert set(_TABELAS) <= existentes

    def test_email_e_unico_sem_diferenciar_caixa(self, pool_postgres):
        with pool_postgres.connection() as conexao:
            _criar_usuario(conexao, email="Ana@Exemplo.com", perfil="u-111111111111")

            with pytest.raises(psycopg.errors.UniqueViolation):
                _criar_usuario(conexao, email="ana@exemplo.com", perfil="u-222222222222")

    def test_perfil_pertence_a_no_maximo_um_usuario(self, pool_postgres):
        with pool_postgres.connection() as conexao:
            _criar_usuario(conexao, email="a@b.com", perfil="u-111111111111")

            with pytest.raises(psycopg.errors.UniqueViolation):
                _criar_usuario(conexao, email="c@d.com", perfil="u-111111111111")

    def test_usuario_exige_perfil_existente(self, pool_postgres):
        with pool_postgres.connection() as conexao:
            with pytest.raises(psycopg.errors.ForeignKeyViolation):
                conexao.execute(
                    "INSERT INTO usuario (id, email, perfil_identificador) VALUES (%s, %s, %s)",
                    (uuid4(), "a@b.com", "perfil-inexistente"),
                )

    def test_finalidade_do_token_so_aceita_valores_conhecidos(self, pool_postgres):
        with pool_postgres.connection() as conexao:
            usuario_id = _criar_usuario(conexao)

            with pytest.raises(psycopg.errors.CheckViolation):
                conexao.execute(
                    "INSERT INTO token_uso_unico (token_hash, usuario_id, finalidade, expira_em)"
                    " VALUES (%s, %s, 'outra', now())",
                    (b"hash", usuario_id),
                )

    def test_remover_usuario_remove_dependentes_em_cascata(self, pool_postgres):
        with pool_postgres.connection() as conexao:
            usuario_id = _criar_usuario(conexao)
            conexao.execute(
                "INSERT INTO identidade_externa (provedor, subject, usuario_id) VALUES ('google', '1', %s)",
                (usuario_id,),
            )
            conexao.execute(
                "INSERT INTO credencial_senha (usuario_id, senha_hash) VALUES (%s, 'hash')", (usuario_id,)
            )
            conexao.execute(
                "INSERT INTO sessao (token_hash, usuario_id, criada_em, ultimo_acesso_em, expira_em)"
                " VALUES (%s, %s, now(), now(), now())",
                (b"sessao", usuario_id),
            )

            conexao.execute("DELETE FROM usuario WHERE id = %s", (usuario_id,))

            restantes = [
                conexao.execute(f"SELECT count(*) FROM {tabela}").fetchone()[0]
                for tabela in ("identidade_externa", "credencial_senha", "sessao")
            ]
        assert restantes == [0, 0, 0]

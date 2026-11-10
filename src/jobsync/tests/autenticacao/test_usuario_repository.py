"""Testes de contrato do UsuarioRepository (fake e PostgreSQL)."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import IdentidadeJaVinculada, UsuarioDuplicado
from jobsync.autenticacao.domain.identidade_externa import IdentidadeExterna
from jobsync.autenticacao.domain.usuario import Usuario

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)


class TestUsuarioRepository:
    def test_busca_por_id_devolve_o_usuario_salvo(self, repositorios, usuario):
        encontrado = repositorios.usuarios.buscar_por_id(usuario.id)

        assert encontrado == usuario

    def test_busca_por_id_inexistente_devolve_none(self, repositorios):
        assert repositorios.usuarios.buscar_por_id(uuid4()) is None

    def test_busca_por_email_ignora_caixa(self, repositorios, usuario):
        encontrado = repositorios.usuarios.buscar_por_email(Email("ANA@exemplo.com"))

        assert encontrado == usuario

    def test_busca_por_email_inexistente_devolve_none(self, repositorios):
        assert repositorios.usuarios.buscar_por_email(Email("x@y.com")) is None

    def test_busca_por_perfil(self, repositorios, usuario):
        assert repositorios.usuarios.buscar_por_perfil("u-aaaaaaaaaaaa") == usuario
        assert repositorios.usuarios.buscar_por_perfil("u-outro") is None

    def test_email_duplicado_gera_erro(self, repositorios, usuario):
        outro = Usuario.novo(Email("ana@exemplo.com"), "u-bbbbbbbbbbbb", AGORA)

        with pytest.raises(UsuarioDuplicado):
            repositorios.usuarios.salvar_novo(outro)

    def test_perfil_ja_associado_a_outro_usuario_gera_erro(self, repositorios, usuario):
        outro = Usuario.novo(Email("bia@exemplo.com"), "u-aaaaaaaaaaaa", AGORA)

        with pytest.raises(UsuarioDuplicado):
            repositorios.usuarios.salvar_novo(outro)

    def test_atualizar_persiste_a_verificacao_do_email(self, repositorios, usuario):
        repositorios.usuarios.atualizar(usuario.verificar_email())

        assert repositorios.usuarios.buscar_por_id(usuario.id).email_verificado is True

    def test_vincular_identidade_permite_buscar_o_usuario(self, repositorios, usuario):
        repositorios.usuarios.vincular_identidade(IdentidadeExterna("google", "sub-1", usuario.id))

        assert repositorios.usuarios.buscar_por_identidade("google", "sub-1") == usuario
        assert repositorios.usuarios.buscar_por_identidade("google", "sub-2") is None

    def test_vincular_a_mesma_identidade_duas_vezes_gera_erro(self, repositorios, usuario):
        identidade = IdentidadeExterna("google", "sub-1", usuario.id)
        repositorios.usuarios.vincular_identidade(identidade)

        with pytest.raises(IdentidadeJaVinculada):
            repositorios.usuarios.vincular_identidade(identidade)

    def test_senha_inicialmente_inexistente(self, repositorios, usuario):
        assert repositorios.usuarios.obter_senha_hash(usuario.id) is None

    def test_definir_senha_hash_substitui_a_anterior(self, repositorios, usuario):
        repositorios.usuarios.definir_senha_hash(usuario.id, "hash-1")
        repositorios.usuarios.definir_senha_hash(usuario.id, "hash-2")

        assert repositorios.usuarios.obter_senha_hash(usuario.id) == "hash-2"

    def test_remover_senha(self, repositorios, usuario):
        repositorios.usuarios.definir_senha_hash(usuario.id, "hash-1")

        repositorios.usuarios.remover_senha(usuario.id)

        assert repositorios.usuarios.obter_senha_hash(usuario.id) is None

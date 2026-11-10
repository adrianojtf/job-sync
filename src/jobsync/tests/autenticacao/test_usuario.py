"""Testes da entidade Usuario e da geração do identificador de perfil."""

from datetime import datetime, timezone
from uuid import UUID

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.usuario import Usuario, novo_identificador_de_perfil

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)


class TestUsuario:
    def test_novo_usuario_nasce_com_email_nao_verificado(self):
        usuario = Usuario.novo(Email("a@b.com"), "u-abc123def456", AGORA, nome="Ana")

        assert usuario.email_verificado is False
        assert usuario.perfil_identificador == "u-abc123def456"
        assert usuario.nome == "Ana"
        assert usuario.criado_em == AGORA
        assert isinstance(usuario.id, UUID)

    def test_verificar_email_devolve_novo_usuario_verificado(self):
        usuario = Usuario.novo(Email("a@b.com"), "u-abc123def456", AGORA)

        verificado = usuario.verificar_email()

        assert verificado.email_verificado is True
        assert verificado.id == usuario.id
        assert usuario.email_verificado is False

    def test_perfil_identificador_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            Usuario.novo(Email("a@b.com"), "  ", AGORA)

    def test_criado_em_sem_fuso_gera_erro(self):
        with pytest.raises(ValueError):
            Usuario.novo(Email("a@b.com"), "u-abc123def456", datetime(2026, 1, 10, 12, 0))

    def test_usuario_e_imutavel(self):
        usuario = Usuario.novo(Email("a@b.com"), "u-abc123def456", AGORA)

        with pytest.raises(Exception):
            usuario.email_verificado = True


class TestNovoIdentificadorDePerfil:
    def test_tem_prefixo_u_e_12_caracteres_hexadecimais(self):
        identificador = novo_identificador_de_perfil()

        assert identificador.startswith("u-")
        assert len(identificador) == 14
        int(identificador[2:], 16)

    def test_gera_valores_diferentes(self):
        assert novo_identificador_de_perfil() != novo_identificador_de_perfil()

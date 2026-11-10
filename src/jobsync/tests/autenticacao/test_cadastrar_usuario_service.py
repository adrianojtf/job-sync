"""Testes do serviço CadastrarUsuario."""

from datetime import timedelta

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import EmailInvalido, SenhaInvalida
from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.domain.token_uso_unico import Finalidade
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.service_layer.cadastrar_usuario.service import CadastrarUsuario

SENHA = "uma-senha-longa-1"


def _servico(ambiente) -> CadastrarUsuario:
    return CadastrarUsuario(
        ambiente.usuarios, ambiente.tokens, ambiente.hasher, ambiente.enviador, ambiente.config, ambiente.relogio
    )


def _consumir(ambiente, email, token=None):
    token = token or ambiente.enviador.ultimo_token(email)
    return ambiente.tokens.consumir(hash_token(token), Finalidade.CONFIRMACAO_EMAIL, ambiente.relogio.agora)


class TestCadastrarUsuario:
    def test_cria_usuario_nao_verificado_com_perfil_proprio(self, ambiente):
        _servico(ambiente).executar("Ana@Exemplo.com", SENHA)

        usuario = ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com"))
        assert usuario.email_verificado is False
        assert usuario.perfil_identificador.startswith("u-")

    def test_nao_ativa_a_senha_antes_da_confirmacao(self, ambiente):
        _servico(ambiente).executar("ana@exemplo.com", SENHA)

        usuario = ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com"))
        assert ambiente.usuarios.obter_senha_hash(usuario.id) is None

    def test_guarda_o_hash_da_senha_na_carga_do_token(self, ambiente):
        _servico(ambiente).executar("ana@exemplo.com", SENHA)

        token = _consumir(ambiente, "ana@exemplo.com")

        assert token.carga == ambiente.hasher.gerar(SENHA)

    def test_envia_confirmacao_com_link_valido_por_24_horas(self, ambiente):
        _servico(ambiente).executar("ana@exemplo.com", SENHA)

        _, assunto, corpo = ambiente.enviador.para("ana@exemplo.com")[0]
        token = _consumir(ambiente, "ana@exemplo.com")
        assert "http://localhost:8080/confirmar-email?token=" in corpo
        assert "onfirm" in assunto
        assert token.expira_em == ambiente.relogio.agora + timedelta(hours=24)

    def test_nao_registra_o_token_em_texto_puro(self, ambiente):
        _servico(ambiente).executar("ana@exemplo.com", SENHA)
        token = ambiente.enviador.ultimo_token("ana@exemplo.com")

        assert hash_token(token) != token.encode()
        assert ambiente.tokens.consumir(token.encode(), Finalidade.CONFIRMACAO_EMAIL, ambiente.relogio.agora) is None

    def test_email_ja_confirmado_nao_altera_a_conta_e_avisa_o_dono(self, ambiente):
        existente = Usuario.novo(Email("ana@exemplo.com"), "u-aaaaaaaaaaaa", ambiente.relogio.agora).verificar_email()
        ambiente.usuarios.salvar_novo(existente)
        ambiente.usuarios.definir_senha_hash(existente.id, "hash::senha-original-1")

        _servico(ambiente).executar("ana@exemplo.com", SENHA)

        assert ambiente.usuarios.obter_senha_hash(existente.id) == "hash::senha-original-1"
        assert ambiente.enviador.ultimo_token("ana@exemplo.com") is None
        assert len(ambiente.enviador.para("ana@exemplo.com")) == 1
        assert "/entrar" in ambiente.enviador.para("ana@exemplo.com")[0][2]

    def test_usuario_pre_criado_pelo_mantenedor_recebe_confirmacao_sem_trocar_de_perfil(self, ambiente):
        legado = Usuario.novo(Email("ana@exemplo.com"), "matheus", ambiente.relogio.agora)
        ambiente.usuarios.salvar_novo(legado)

        _servico(ambiente).executar("ana@exemplo.com", SENHA)

        assert ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com")).perfil_identificador == "matheus"
        assert ambiente.enviador.ultimo_token("ana@exemplo.com") is not None

    def test_novo_cadastro_invalida_o_link_anterior(self, ambiente):
        _servico(ambiente).executar("ana@exemplo.com", "primeira-senha-12")
        primeiro = ambiente.enviador.ultimo_token("ana@exemplo.com")

        _servico(ambiente).executar("ana@exemplo.com", "segunda-senha-34")

        assert _consumir(ambiente, "ana@exemplo.com", primeiro) is None
        assert _consumir(ambiente, "ana@exemplo.com").carga == ambiente.hasher.gerar("segunda-senha-34")

    def test_email_invalido_gera_erro(self, ambiente):
        with pytest.raises(EmailInvalido):
            _servico(ambiente).executar("nao-e-email", SENHA)

    def test_senha_fora_da_politica_gera_erro_e_nao_cria_usuario(self, ambiente):
        with pytest.raises(SenhaInvalida):
            _servico(ambiente).executar("ana@exemplo.com", "curta")

        assert ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com")) is None
        assert ambiente.enviador.enviados == []

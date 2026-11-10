"""Testes do serviço EntrarComSenha."""

from datetime import timedelta

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import CredenciaisInvalidas, LimiteTentativasExcedido
from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao
from jobsync.autenticacao.service_layer.entrar_com_senha.service import EntrarComSenha

SENHA = "uma-senha-longa-1"


@pytest.fixture
def servico(ambiente):
    return EntrarComSenha(
        ambiente.usuarios,
        ambiente.limites,
        ambiente.hasher,
        EmitirSessao(ambiente.sessoes, ambiente.config, ambiente.relogio),
        ambiente.config,
        ambiente.relogio,
    )


@pytest.fixture
def usuario(ambiente):
    ativo = Usuario.novo(Email("ana@exemplo.com"), "u-aaaaaaaaaaaa", ambiente.relogio.agora).verificar_email()
    ambiente.usuarios.salvar_novo(ativo)
    ambiente.usuarios.definir_senha_hash(ativo.id, ambiente.hasher.gerar(SENHA))
    return ativo


class TestEntrarComSenha:
    def test_credenciais_corretas_criam_sessao(self, ambiente, servico, usuario):
        resultado = servico.executar("Ana@Exemplo.com", SENHA, ip="10.0.0.1")

        assert resultado.usuario == usuario
        assert ambiente.sessoes.buscar(hash_token(resultado.token)).usuario_id == usuario.id

    def test_senha_errada_gera_credenciais_invalidas(self, servico, usuario):
        with pytest.raises(CredenciaisInvalidas):
            servico.executar("ana@exemplo.com", "senha-errada-123", ip="10.0.0.1")

    def test_email_desconhecido_gera_o_mesmo_erro(self, servico):
        with pytest.raises(CredenciaisInvalidas):
            servico.executar("ninguem@exemplo.com", SENHA, ip="10.0.0.1")

    def test_email_malformado_gera_o_mesmo_erro(self, servico):
        with pytest.raises(CredenciaisInvalidas):
            servico.executar("isto-nao-e-email", SENHA, ip="10.0.0.1")

    def test_usuario_sem_senha_ativada_gera_o_mesmo_erro(self, ambiente, servico):
        pendente = Usuario.novo(Email("pendente@exemplo.com"), "u-bbbbbbbbbbbb", ambiente.relogio.agora)
        ambiente.usuarios.salvar_novo(pendente)

        with pytest.raises(CredenciaisInvalidas):
            servico.executar("pendente@exemplo.com", SENHA, ip="10.0.0.1")

    def test_bloqueia_apos_5_falhas_mesmo_com_a_senha_certa(self, servico, usuario):
        for _ in range(5):
            with pytest.raises(CredenciaisInvalidas):
                servico.executar("ana@exemplo.com", "senha-errada-123", ip="10.0.0.1")

        with pytest.raises(LimiteTentativasExcedido) as erro:
            servico.executar("ana@exemplo.com", SENHA, ip="10.0.0.2")

        assert erro.value.retry_after_segundos == 15 * 60

    def test_poucas_falhas_de_um_ip_nao_bloqueiam_os_demais_usuarios_do_mesmo_ip(self, servico, usuario):
        for indice in range(5):
            with pytest.raises(CredenciaisInvalidas):
                servico.executar(f"alvo{indice}@exemplo.com", SENHA, ip="10.0.0.9")

        assert servico.executar("ana@exemplo.com", SENHA, ip="10.0.0.9").usuario == usuario

    def test_bloqueio_por_ip_vale_para_qualquer_email_ao_passar_do_limite_do_ip(self, servico, usuario):
        for indice in range(30):
            with pytest.raises(CredenciaisInvalidas):
                servico.executar(f"alvo{indice}@exemplo.com", SENHA, ip="10.0.0.9")

        with pytest.raises(LimiteTentativasExcedido):
            servico.executar("ana@exemplo.com", SENHA, ip="10.0.0.9")

    def test_desbloqueia_depois_do_periodo(self, ambiente, servico, usuario):
        for _ in range(5):
            with pytest.raises(CredenciaisInvalidas):
                servico.executar("ana@exemplo.com", "senha-errada-123", ip="10.0.0.1")
        ambiente.relogio.avancar(minutes=15)

        assert servico.executar("ana@exemplo.com", SENHA, ip="10.0.0.3").usuario == usuario

    def test_sucesso_zera_as_falhas_do_email(self, ambiente, servico, usuario):
        for _ in range(4):
            with pytest.raises(CredenciaisInvalidas):
                servico.executar("ana@exemplo.com", "senha-errada-123", ip="10.0.0.1")
        servico.executar("ana@exemplo.com", SENHA, ip="10.0.0.1")

        with pytest.raises(CredenciaisInvalidas):
            servico.executar("ana@exemplo.com", "senha-errada-123", ip="10.0.0.5")

    def test_funciona_sem_ip(self, servico, usuario):
        assert servico.executar("ana@exemplo.com", SENHA, ip=None).usuario == usuario

    def test_email_desconhecido_tambem_conta_para_o_bloqueio(self, servico):
        for _ in range(5):
            with pytest.raises(CredenciaisInvalidas):
                servico.executar("ninguem@exemplo.com", SENHA, ip=None)

        with pytest.raises(LimiteTentativasExcedido):
            servico.executar("ninguem@exemplo.com", SENHA, ip=None)

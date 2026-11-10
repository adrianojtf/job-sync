"""Testes do serviço AssociarEmailAPerfil (migração dos perfis legados)."""

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import (
    EmailEmUso,
    EmailInvalido,
    PerfilInexistente,
    PerfilJaAssociado,
)
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.service_layer.associar_email_a_perfil.service import (
    AssociarEmailAPerfil,
    ResultadoAssociacao,
)
from jobsync.perfil.adapters import PerfilRepositoryFake


@pytest.fixture
def perfis():
    repositorio = PerfilRepositoryFake()
    repositorio.criar("matheus")
    return repositorio


@pytest.fixture
def servico(ambiente, perfis):
    return AssociarEmailAPerfil(ambiente.usuarios, perfis, ambiente.relogio)


class TestAssociarEmailAPerfil:
    def test_cria_usuario_nao_verificado_para_o_perfil_legado(self, ambiente, servico):
        resultado = servico.executar("matheus", "Matheus@Exemplo.com")

        usuario = ambiente.usuarios.buscar_por_perfil("matheus")
        assert resultado is ResultadoAssociacao.ASSOCIADO
        assert usuario.email == Email("matheus@exemplo.com")
        assert usuario.email_verificado is False

    def test_nao_define_senha_nem_identidade(self, ambiente, servico):
        servico.executar("matheus", "matheus@exemplo.com")

        usuario = ambiente.usuarios.buscar_por_perfil("matheus")
        assert ambiente.usuarios.obter_senha_hash(usuario.id) is None

    def test_repetir_o_mesmo_par_e_idempotente(self, ambiente, servico):
        servico.executar("matheus", "matheus@exemplo.com")
        primeiro = ambiente.usuarios.buscar_por_perfil("matheus")

        resultado = servico.executar("matheus", "MATHEUS@exemplo.com")

        assert resultado is ResultadoAssociacao.JA_ASSOCIADO
        assert ambiente.usuarios.buscar_por_perfil("matheus") == primeiro

    def test_perfil_inexistente_gera_erro(self, servico):
        with pytest.raises(PerfilInexistente):
            servico.executar("ninguem", "matheus@exemplo.com")

    def test_email_invalido_gera_erro(self, servico):
        with pytest.raises(EmailInvalido):
            servico.executar("matheus", "isto-nao-e-email")

    def test_perfil_ja_associado_a_outro_email_gera_erro(self, ambiente, servico):
        servico.executar("matheus", "matheus@exemplo.com")

        with pytest.raises(PerfilJaAssociado):
            servico.executar("matheus", "outro@exemplo.com")

    def test_email_de_outro_usuario_gera_erro_e_nao_altera_nada(self, ambiente, perfis, servico):
        perfis.criar("ana")
        ambiente.usuarios.salvar_novo(Usuario.novo(Email("matheus@exemplo.com"), "ana", ambiente.relogio.agora))

        with pytest.raises(EmailEmUso):
            servico.executar("matheus", "matheus@exemplo.com")

        assert ambiente.usuarios.buscar_por_perfil("matheus") is None


class TestAssociacaoSeguidaDeLoginGoogle:
    def test_primeiro_login_com_email_verificado_completa_o_vinculo_no_perfil_legado(self, ambiente, servico):
        from jobsync.autenticacao.domain.provedor_identidade import IdentidadeAutenticada
        from jobsync.autenticacao.service_layer.concluir_login_oauth.service import ConcluirLoginOAuth
        from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao
        from jobsync.autenticacao.service_layer.iniciar_login_oauth.service import IniciarLoginOAuth
        from jobsync.tests.autenticacao.dobles import ProvedorFalso

        provedor = ProvedorFalso()
        provedor.identidade = IdentidadeAutenticada("google", "sub-1", "matheus@exemplo.com", True, "Matheus")
        servico.executar("matheus", "matheus@exemplo.com")
        iniciar = IniciarLoginOAuth({"google": provedor}, ambiente.estados, ambiente.config, ambiente.relogio)
        concluir = ConcluirLoginOAuth(
            {"google": provedor},
            ambiente.estados,
            ambiente.usuarios,
            ambiente.tokens,
            EmitirSessao(ambiente.sessoes, ambiente.config, ambiente.relogio),
            ambiente.config,
            ambiente.relogio,
        )
        estado = iniciar.executar("google", "/").estado

        usuario = concluir.executar("google", "codigo", estado, estado).sessao.usuario

        assert usuario.perfil_identificador == "matheus"
        assert usuario.email_verificado is True

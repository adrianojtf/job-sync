"""Testes do serviço ConcluirLoginOAuth."""

from datetime import timedelta

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import (
    EmailNaoVerificado,
    EstadoOAuthInvalido,
    ProvedorDesconhecido,
    ProvedorIndisponivel,
)
from jobsync.autenticacao.domain.provedor_identidade import IdentidadeAutenticada
from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.domain.token_uso_unico import Finalidade, TokenUsoUnico
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.service_layer.concluir_login_oauth.service import ConcluirLoginOAuth
from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao
from jobsync.autenticacao.service_layer.iniciar_login_oauth.service import IniciarLoginOAuth
from jobsync.tests.autenticacao.dobles import ProvedorFalso


def _identidade(email="ana@exemplo.com", verificado=True, subject="sub-1", nome="Ana Souza"):
    return IdentidadeAutenticada("google", subject, email, verificado, nome)


@pytest.fixture
def provedor():
    falso = ProvedorFalso()
    falso.identidade = _identidade()
    return falso


@pytest.fixture
def iniciar(ambiente, provedor):
    return IniciarLoginOAuth({"google": provedor}, ambiente.estados, ambiente.config, ambiente.relogio)


@pytest.fixture
def concluir(ambiente, provedor):
    return ConcluirLoginOAuth(
        {"google": provedor, "outro": ProvedorFalso("outro")},
        ambiente.estados,
        ambiente.usuarios,
        ambiente.tokens,
        EmitirSessao(ambiente.sessoes, ambiente.config, ambiente.relogio),
        ambiente.config,
        ambiente.relogio,
    )


def _login(iniciar, concluir, destino="/vagas"):
    estado = iniciar.executar("google", destino).estado
    return concluir.executar("google", "codigo", estado, estado)


class TestConcluirLoginOAuth:
    def test_usuario_novo_recebe_perfil_proprio_e_email_verificado(self, ambiente, iniciar, concluir):
        resultado = _login(iniciar, concluir)

        usuario = ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com"))
        assert resultado.sessao.usuario == usuario
        assert usuario.email_verificado is True
        assert usuario.perfil_identificador.startswith("u-")
        assert usuario.nome == "Ana Souza"

    def test_cria_sessao_valida(self, ambiente, iniciar, concluir):
        resultado = _login(iniciar, concluir)

        sessao = ambiente.sessoes.buscar(hash_token(resultado.sessao.token))
        assert sessao.usuario_id == resultado.sessao.usuario.id

    def test_devolve_o_destino_guardado_no_inicio(self, iniciar, concluir):
        assert _login(iniciar, concluir, "/candidaturas").destino == "/candidaturas"

    def test_segundo_login_reutiliza_o_mesmo_usuario(self, iniciar, concluir):
        primeiro = _login(iniciar, concluir).sessao.usuario

        segundo = _login(iniciar, concluir).sessao.usuario

        assert segundo == primeiro

    def test_identidade_ja_vinculada_entra_mesmo_sem_email_verificado(self, provedor, iniciar, concluir):
        primeiro = _login(iniciar, concluir).sessao.usuario
        provedor.identidade = _identidade(verificado=False)

        assert _login(iniciar, concluir).sessao.usuario == primeiro

    def test_vincula_ao_perfil_legado_pre_criado_pelo_mantenedor(self, ambiente, iniciar, concluir):
        legado = Usuario.novo(Email("ana@exemplo.com"), "matheus", ambiente.relogio.agora)
        ambiente.usuarios.salvar_novo(legado)

        usuario = _login(iniciar, concluir).sessao.usuario

        assert usuario.id == legado.id
        assert usuario.perfil_identificador == "matheus"
        assert usuario.email_verificado is True
        assert ambiente.usuarios.buscar_por_identidade("google", "sub-1") == usuario

    def test_email_do_google_com_caixa_diferente_encontra_o_legado(self, ambiente, provedor, iniciar, concluir):
        legado = Usuario.novo(Email("ana@exemplo.com"), "matheus", ambiente.relogio.agora)
        ambiente.usuarios.salvar_novo(legado)
        provedor.identidade = _identidade(email="Ana@Exemplo.COM")

        assert _login(iniciar, concluir).sessao.usuario.perfil_identificador == "matheus"

    def test_vincula_ao_usuario_que_ja_tinha_senha(self, ambiente, iniciar, concluir):
        existente = Usuario.novo(Email("ana@exemplo.com"), "u-aaaaaaaaaaaa", ambiente.relogio.agora).verificar_email()
        ambiente.usuarios.salvar_novo(existente)
        ambiente.usuarios.definir_senha_hash(existente.id, "hash::senha-do-dono-12")

        usuario = _login(iniciar, concluir).sessao.usuario

        assert usuario.id == existente.id
        assert ambiente.usuarios.obter_senha_hash(existente.id) == "hash::senha-do-dono-12"

    def test_descarta_links_de_confirmacao_pendentes_ao_vincular(self, ambiente, iniciar, concluir):
        legado = Usuario.novo(Email("ana@exemplo.com"), "matheus", ambiente.relogio.agora)
        ambiente.usuarios.salvar_novo(legado)
        ambiente.tokens.salvar(
            TokenUsoUnico.emitir(
                hash_token("link-do-atacante"),
                legado.id,
                Finalidade.CONFIRMACAO_EMAIL,
                ambiente.relogio.agora,
                timedelta(hours=24),
                carga="hash::senha-do-atacante",
            )
        )

        _login(iniciar, concluir)

        consumido = ambiente.tokens.consumir(
            hash_token("link-do-atacante"), Finalidade.CONFIRMACAO_EMAIL, ambiente.relogio.agora
        )
        assert consumido is None

    def test_email_nao_verificado_e_recusado_e_nao_cria_usuario(self, ambiente, provedor, iniciar, concluir):
        provedor.identidade = _identidade(verificado=False)

        with pytest.raises(EmailNaoVerificado):
            _login(iniciar, concluir)

        assert ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com")) is None

    def test_email_nao_verificado_nao_assume_perfil_legado(self, ambiente, provedor, iniciar, concluir):
        legado = Usuario.novo(Email("ana@exemplo.com"), "matheus", ambiente.relogio.agora)
        ambiente.usuarios.salvar_novo(legado)
        provedor.identidade = _identidade(verificado=False)

        with pytest.raises(EmailNaoVerificado):
            _login(iniciar, concluir)

        assert ambiente.usuarios.buscar_por_identidade("google", "sub-1") is None
        assert ambiente.usuarios.buscar_por_id(legado.id).email_verificado is False

    def test_envia_ao_provedor_o_codigo_o_verificador_e_o_nonce_guardados(self, ambiente, provedor, iniciar, concluir):
        estado = iniciar.executar("google", "/").estado
        guardado_nonce = provedor.ultima_url_autorizacao["nonce"]

        concluir.executar("google", "codigo-123", estado, estado)

        codigo, verificador, nonce = provedor.chamadas[0]
        assert codigo == "codigo-123"
        assert nonce == guardado_nonce
        assert 43 <= len(verificador) <= 128

    def test_cookie_diferente_do_estado_e_recusado_sem_chamar_o_provedor(self, provedor, iniciar, concluir):
        estado = iniciar.executar("google", "/").estado

        with pytest.raises(EstadoOAuthInvalido):
            concluir.executar("google", "codigo", estado, "outro-valor")

        assert provedor.chamadas == []

    def test_cookie_ausente_e_recusado(self, iniciar, concluir):
        estado = iniciar.executar("google", "/").estado

        with pytest.raises(EstadoOAuthInvalido):
            concluir.executar("google", "codigo", estado, None)

    def test_estado_desconhecido_e_recusado(self, concluir):
        with pytest.raises(EstadoOAuthInvalido):
            concluir.executar("google", "codigo", "forjado", "forjado")

    def test_estado_so_vale_uma_vez(self, iniciar, concluir):
        estado = iniciar.executar("google", "/").estado
        concluir.executar("google", "codigo", estado, estado)

        with pytest.raises(EstadoOAuthInvalido):
            concluir.executar("google", "codigo", estado, estado)

    def test_estado_expirado_e_recusado(self, ambiente, iniciar, concluir):
        estado = iniciar.executar("google", "/").estado
        ambiente.relogio.avancar(minutes=10)

        with pytest.raises(EstadoOAuthInvalido):
            concluir.executar("google", "codigo", estado, estado)

    def test_estado_de_outro_provedor_e_recusado(self, iniciar, concluir):
        estado = iniciar.executar("google", "/").estado

        with pytest.raises(EstadoOAuthInvalido):
            concluir.executar("outro", "codigo", estado, estado)

    def test_provedor_desconhecido_gera_erro(self, concluir):
        with pytest.raises(ProvedorDesconhecido):
            concluir.executar("facebook", "codigo", "x", "x")

    def test_falha_do_provedor_propaga_e_nao_cria_usuario(self, ambiente, provedor, iniciar, concluir):
        provedor.erro = ProvedorIndisponivel("fora do ar")

        with pytest.raises(ProvedorIndisponivel):
            _login(iniciar, concluir)

        assert ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com")) is None

    def test_email_malformado_vindo_do_provedor_e_tratado_como_falha_do_provedor(self, provedor, iniciar, concluir):
        provedor.identidade = _identidade(email="isto-nao-e-email")

        with pytest.raises(ProvedorIndisponivel):
            _login(iniciar, concluir)

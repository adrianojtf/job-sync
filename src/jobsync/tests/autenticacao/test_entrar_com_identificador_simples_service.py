"""Testes do serviço EntrarComIdentificadorSimples (login legado, só para desenvolvimento)."""

import pytest

from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao
from jobsync.autenticacao.service_layer.entrar_com_identificador_simples.service import (
    EntrarComIdentificadorSimples,
)


@pytest.fixture
def servico(ambiente):
    return EntrarComIdentificadorSimples(
        ambiente.usuarios,
        EmitirSessao(ambiente.sessoes, ambiente.config, ambiente.relogio),
        ambiente.relogio,
    )


class TestEntrarComIdentificadorSimples:
    def test_cria_usuario_cujo_perfil_e_o_proprio_identificador(self, ambiente, servico):
        resultado = servico.executar("matheus")

        assert resultado.usuario.perfil_identificador == "matheus"
        assert resultado.usuario.email_verificado is True
        assert ambiente.sessoes.buscar(hash_token(resultado.token)).usuario_id == resultado.usuario.id

    def test_reutiliza_o_usuario_na_segunda_entrada(self, servico):
        primeiro = servico.executar("matheus").usuario

        segundo = servico.executar("matheus").usuario

        assert segundo == primeiro

    def test_identificadores_diferentes_geram_usuarios_diferentes(self, servico):
        assert servico.executar("ana").usuario.id != servico.executar("beto").usuario.id

    def test_aceita_identificador_com_espacos_e_acentos(self, servico):
        resultado = servico.executar("João da Silva")

        assert resultado.usuario.perfil_identificador == "João da Silva"

    def test_identificadores_parecidos_nao_colidem(self, servico):
        assert servico.executar("A B").usuario.id != servico.executar("a-b").usuario.id

    def test_entra_no_perfil_legado_que_ja_tem_usuario_associado(self, ambiente, servico):
        from jobsync.autenticacao.domain.email import Email
        from jobsync.autenticacao.domain.usuario import Usuario

        legado = Usuario.novo(Email("ana@exemplo.com"), "ana", ambiente.relogio.agora)
        ambiente.usuarios.salvar_novo(legado)

        assert servico.executar("ana").usuario.id == legado.id

    @pytest.mark.parametrize("identificador", ["", "   "])
    def test_identificador_vazio_gera_erro(self, servico, identificador):
        with pytest.raises(ValueError):
            servico.executar(identificador)

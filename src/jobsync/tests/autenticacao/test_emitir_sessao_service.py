"""Testes do serviço EmitirSessao."""

from datetime import timedelta
from uuid import uuid4

from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao


class TestEmitirSessao:
    def test_devolve_token_e_persiste_apenas_o_hash(self, ambiente):
        servico = EmitirSessao(ambiente.sessoes, ambiente.config, ambiente.relogio)
        usuario_id = uuid4()

        token = servico.executar(usuario_id)

        sessao = ambiente.sessoes.buscar(hash_token(token))
        assert sessao.usuario_id == usuario_id
        assert sessao.token_hash != token.encode()

    def test_define_expiracao_absoluta_pela_configuracao(self, ambiente):
        servico = EmitirSessao(ambiente.sessoes, ambiente.config, ambiente.relogio)

        token = servico.executar(uuid4())

        sessao = ambiente.sessoes.buscar(hash_token(token))
        assert sessao.expira_em == ambiente.relogio.agora + timedelta(days=30)

    def test_cada_chamada_gera_um_token_diferente(self, ambiente):
        servico = EmitirSessao(ambiente.sessoes, ambiente.config, ambiente.relogio)
        usuario_id = uuid4()

        assert servico.executar(usuario_id) != servico.executar(usuario_id)

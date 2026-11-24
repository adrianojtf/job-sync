from jobsync.vaga import (
    FonteVagaNaoSuportada,
    LeituraVagaIndisponivel,
    LimiteLeituraVagaExcedido,
    MotivoLeituraIndisponivel,
)


class TestLeituraVagaIndisponivel:
    def test_expoe_o_motivo_e_uma_mensagem_em_linguagem_simples(self):
        erro = LeituraVagaIndisponivel(MotivoLeituraIndisponivel.BLOQUEADA)

        assert erro.motivo is MotivoLeituraIndisponivel.BLOQUEADA
        assert "cole o texto" in str(erro).lower()

    def test_cada_motivo_tem_mensagem_propria(self):
        mensagens = {str(LeituraVagaIndisponivel(motivo)) for motivo in MotivoLeituraIndisponivel}

        assert len(mensagens) == len(MotivoLeituraIndisponivel)


class TestLimiteLeituraVagaExcedido:
    def test_expoe_o_tempo_para_nova_tentativa(self):
        erro = LimiteLeituraVagaExcedido(segundos_para_nova_tentativa=42)

        assert erro.segundos_para_nova_tentativa == 42


class TestFonteVagaNaoSuportada:
    def test_expoe_mensagem_informada(self):
        erro = FonteVagaNaoSuportada("A leitura de links do LinkedIn está desativada.")

        assert "LinkedIn" in str(erro)

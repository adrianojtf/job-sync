import pytest

from jobsync.shared_kernel.adapters.cliente_http_seguro import MotivoFalhaHttp
from jobsync.vaga import MotivoLeituraIndisponivel
from jobsync.vaga.adapters.motivos_leitura import (
    motivo_por_falha_http,
    motivo_por_status_http,
)


class TestMotivoPorStatusHttp:
    @pytest.mark.parametrize("status", [401, 403, 429, 451])
    def test_status_de_bloqueio(self, status):
        assert motivo_por_status_http(status) is MotivoLeituraIndisponivel.BLOQUEADA

    @pytest.mark.parametrize("status", [404, 410])
    def test_status_de_vaga_inexistente(self, status):
        assert motivo_por_status_http(status) is MotivoLeituraIndisponivel.NAO_ENCONTRADA

    @pytest.mark.parametrize("status", [500, 502, 503, 504])
    def test_status_de_falha_do_servidor(self, status):
        assert motivo_por_status_http(status) is MotivoLeituraIndisponivel.FALHA_DE_REDE

    @pytest.mark.parametrize("status", [204, 400, 418])
    def test_outros_status_nao_trazem_dados(self, status):
        assert motivo_por_status_http(status) is MotivoLeituraIndisponivel.SEM_DADOS


class TestMotivoPorFalhaHttp:
    @pytest.mark.parametrize(
        "falha, esperado",
        [
            (MotivoFalhaHttp.ENDERECO_RECUSADO, MotivoLeituraIndisponivel.ENDERECO_RECUSADO),
            (MotivoFalhaHttp.TEMPO_ESGOTADO, MotivoLeituraIndisponivel.TEMPO_ESGOTADO),
            (MotivoFalhaHttp.FALHA_DE_REDE, MotivoLeituraIndisponivel.FALHA_DE_REDE),
            (MotivoFalhaHttp.EXCESSO_REDIRECIONAMENTOS, MotivoLeituraIndisponivel.FALHA_DE_REDE),
            (MotivoFalhaHttp.TAMANHO_EXCEDIDO, MotivoLeituraIndisponivel.SEM_DADOS),
        ],
    )
    def test_traduz_a_falha_http_para_o_motivo_de_dominio(self, falha, esperado):
        assert motivo_por_falha_http(falha) is esperado

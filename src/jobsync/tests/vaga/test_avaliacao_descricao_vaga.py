from jobsync.shared_kernel.domain import ResultadoDimensaoAvaliacao
from jobsync.vaga import AvaliacaoDescricaoVaga


def test_avaliacao_descricao_vaga_calcula_media_das_quatro_dimensoes():
    avaliacao = AvaliacaoDescricaoVaga(
        completude=ResultadoDimensaoAvaliacao(50, "parcial", 0.8),
        clareza=ResultadoDimensaoAvaliacao(60, "parcial", 0.8),
        relevancia=ResultadoDimensaoAvaliacao(70, "adequado", 0.8),
        inclusao=ResultadoDimensaoAvaliacao(80, "bom", 0.8),
    )

    assert avaliacao.score == 65

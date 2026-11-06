from jobsync.curriculo.domain.avaliacao_experiencia import (
    AvaliacaoExperiencia,
    ExperienciaParaAvaliacao,
)
from jobsync.shared_kernel.domain import ResultadoDimensaoAvaliacao


def test_avaliacao_experiencia_calcula_media_das_quatro_dimensoes():
    avaliacao = AvaliacaoExperiencia(
        clareza_escrita=ResultadoDimensaoAvaliacao(50, "parcial", 0.8),
        qualidade_detalhe=ResultadoDimensaoAvaliacao(60, "parcial", 0.8),
        aderencia_vaga=ResultadoDimensaoAvaliacao(70, "adequado", 0.8),
        consistencia_textual=ResultadoDimensaoAvaliacao(80, "bom", 0.8),
    )

    assert avaliacao.score == 65

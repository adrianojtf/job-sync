import pytest

from jobsync.curriculo import (
    AvaliacaoExperiencia,
    ExperienciaParaAvaliacao,
)
from jobsync.curriculo.domain.avaliador_experiencia_port import (
    AvaliadorExperienciaPort,
)
from jobsync.curriculo.service_layer.avaliar_experiencia import (
    AvaliarExperiencia,
    AvaliarExperienciaInputDto,
    AvaliacaoExperienciaIndisponivel,
)
from jobsync.shared_kernel.domain import ResultadoDimensaoAvaliacao


def _avaliacao() -> AvaliacaoExperiencia:
    dimensao = ResultadoDimensaoAvaliacao(75, "adequado", 0.85)
    return AvaliacaoExperiencia(
        clareza_escrita=dimensao,
        qualidade_detalhe=dimensao,
        aderencia_vaga=dimensao,
        consistencia_textual=dimensao,
    )


class AvaliadorExperienciaFake(AvaliadorExperienciaPort):
    def __init__(self, resultado=None, erro=None):
        self.resultado = resultado
        self.erro = erro
        self.experiencia_recebida = None
        self.vaga_recebida = None

    def avaliar(self, experiencia, descricao_vaga):
        self.experiencia_recebida = experiencia
        self.vaga_recebida = descricao_vaga
        if self.erro is not None:
            raise self.erro
        return self.resultado


class TestAvaliarExperiencia:
    def test_delega_experiencia_e_vaga_e_retorna_resultado(self):
        experiencia = ExperienciaParaAvaliacao(
            descricao="Desenvolvi serviços Python.",
            cargo="Desenvolvedora",
            empresa="TechCorp",
            periodo="2022-2025",
        )
        avaliacao = _avaliacao()
        avaliador = AvaliadorExperienciaFake(resultado=avaliacao)
        servico = AvaliarExperiencia(avaliador)

        resultado = servico.executar(
            AvaliarExperienciaInputDto(
                experiencia=experiencia,
                descricao_vaga="Vaga backend Python.",
            )
        )

        assert resultado is avaliacao
        assert avaliador.experiencia_recebida is experiencia
        assert avaliador.vaga_recebida == "Vaga backend Python."

    def test_rejeita_experiencia_sem_descricao_sem_chamar_provedor(self):
        avaliador = AvaliadorExperienciaFake(resultado=_avaliacao())
        servico = AvaliarExperiencia(avaliador)

        with pytest.raises(ValueError, match="texto da experiência"):
            servico.executar(
                AvaliarExperienciaInputDto(
                    experiencia=ExperienciaParaAvaliacao(descricao=" "),
                    descricao_vaga="Vaga backend.",
                )
            )

        assert avaliador.experiencia_recebida is None

    @pytest.mark.parametrize("descricao_vaga", ["", "   "])
    def test_rejeita_vaga_vazia_sem_chamar_provedor(self, descricao_vaga):
        avaliador = AvaliadorExperienciaFake(resultado=_avaliacao())
        servico = AvaliarExperiencia(avaliador)

        with pytest.raises(ValueError, match="descrição da vaga-alvo é obrigatória"):
            servico.executar(
                AvaliarExperienciaInputDto(
                    experiencia=ExperienciaParaAvaliacao(descricao="Experiência."),
                    descricao_vaga=descricao_vaga,
                )
            )

        assert avaliador.experiencia_recebida is None

    @pytest.mark.parametrize(
        "erro",
        [RuntimeError("falha de rede"), ValueError("resposta estruturada inválida")],
    )
    def test_traduz_falhas_do_provedor_para_excecao_da_aplicacao(self, erro):
        servico = AvaliarExperiencia(AvaliadorExperienciaFake(erro=erro))

        with pytest.raises(AvaliacaoExperienciaIndisponivel):
            servico.executar(
                AvaliarExperienciaInputDto(
                    experiencia=ExperienciaParaAvaliacao(descricao="Experiência."),
                    descricao_vaga="Vaga backend.",
                )
            )

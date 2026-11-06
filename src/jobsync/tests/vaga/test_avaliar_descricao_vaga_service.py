import pytest

from jobsync.shared_kernel.domain import ResultadoDimensaoAvaliacao
from jobsync.vaga.domain.avaliacao_descricao_vaga import AvaliacaoDescricaoVaga
from jobsync.vaga.service_layer.avaliar_descricao_vaga import (
    AvaliarDescricaoVaga,
    AvaliarDescricaoVagaInputDto,
    AvaliacaoDescricaoVagaIndisponivel,
)


def _avaliacao() -> AvaliacaoDescricaoVaga:
    dimensao = ResultadoDimensaoAvaliacao(75, "adequado", 0.85)
    return AvaliacaoDescricaoVaga(
        completude=dimensao,
        clareza=dimensao,
        relevancia=dimensao,
        inclusao=dimensao,
    )


class AvaliadorFake:
    def __init__(self, resultado=None, erro=None):
        self.resultado = resultado
        self.erro = erro
        self.descricao_recebida = None

    def avaliar(self, descricao_vaga: str) -> AvaliacaoDescricaoVaga:
        self.descricao_recebida = descricao_vaga
        if self.erro is not None:
            raise self.erro
        return self.resultado


class TestAvaliarDescricaoVaga:
    def test_delega_avaliacao_e_retorna_resultado(self):
        avaliacao = _avaliacao()
        avaliador = AvaliadorFake(resultado=avaliacao)
        servico = AvaliarDescricaoVaga(avaliador)
        descricao = "Pessoa desenvolvedora Python."

        resultado = servico.executar(AvaliarDescricaoVagaInputDto(descricao))

        assert resultado is avaliacao
        assert avaliador.descricao_recebida == descricao

    @pytest.mark.parametrize("descricao", ["", "   "])
    def test_rejeita_descricao_vazia_sem_chamar_provedor(self, descricao):
        avaliador = AvaliadorFake(resultado=_avaliacao())
        servico = AvaliarDescricaoVaga(avaliador)

        with pytest.raises(ValueError, match="descrição da vaga é obrigatório"):
            servico.executar(AvaliarDescricaoVagaInputDto(descricao))

        assert avaliador.descricao_recebida is None

    @pytest.mark.parametrize(
        "erro",
        [
            RuntimeError("falha de rede"),
            ValueError("resposta estruturada inválida"),
        ],
    )
    def test_traduz_falhas_do_provedor_para_excecao_da_aplicacao(self, erro):
        servico = AvaliarDescricaoVaga(AvaliadorFake(erro=erro))

        with pytest.raises(AvaliacaoDescricaoVagaIndisponivel):
            servico.executar(AvaliarDescricaoVagaInputDto("Descrição válida."))

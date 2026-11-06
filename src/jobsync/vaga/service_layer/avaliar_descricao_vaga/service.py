"""Caso de uso para avaliação estruturada de uma descrição de vaga."""
from __future__ import annotations

from jobsync.vaga.domain.avaliacao_descricao_vaga import AvaliacaoDescricaoVaga
from jobsync.vaga.domain.avaliador_descricao_vaga_port import AvaliadorDescricaoVagaPort
from jobsync.vaga.service_layer.avaliar_descricao_vaga.dtos import (
    AvaliarDescricaoVagaInputDto,
)
from jobsync.vaga.service_layer.avaliar_descricao_vaga.exceptions import (
    AvaliacaoDescricaoVagaIndisponivel,
)
from jobsync.vaga.service_layer.avaliar_descricao_vaga.validator import (
    AvaliarDescricaoVagaInputValidator,
)


class AvaliarDescricaoVaga:
    def __init__(self, avaliador: AvaliadorDescricaoVagaPort) -> None:
        self._avaliador = avaliador

    def executar(self, input_dto: AvaliarDescricaoVagaInputDto) -> AvaliacaoDescricaoVaga:
        AvaliarDescricaoVagaInputValidator.validar(input_dto)
        try:
            return self._avaliador.avaliar(input_dto.descricao_vaga)
        except (RuntimeError, ValueError) as erro:
            raise AvaliacaoDescricaoVagaIndisponivel() from erro

"""Caso de uso para avaliação contextualizada de uma experiência profissional."""
from __future__ import annotations

from jobsync.curriculo.domain.avaliacao_experiencia import AvaliacaoExperiencia
from jobsync.curriculo.domain.avaliador_experiencia_port import AvaliadorExperienciaPort
from jobsync.curriculo.service_layer.avaliar_experiencia.dtos import (
    AvaliarExperienciaInputDto,
)
from jobsync.curriculo.service_layer.avaliar_experiencia.exceptions import (
    AvaliacaoExperienciaIndisponivel,
)
from jobsync.curriculo.service_layer.avaliar_experiencia.validator import (
    AvaliarExperienciaInputValidator,
)


class AvaliarExperiencia:
    def __init__(self, avaliador: AvaliadorExperienciaPort) -> None:
        self._avaliador = avaliador

    def executar(self, input_dto: AvaliarExperienciaInputDto) -> AvaliacaoExperiencia:
        AvaliarExperienciaInputValidator.validar(input_dto)
        try:
            return self._avaliador.avaliar(
                experiencia=input_dto.experiencia,
                descricao_vaga=input_dto.descricao_vaga,
            )
        except (RuntimeError, ValueError) as erro:
            raise AvaliacaoExperienciaIndisponivel() from erro

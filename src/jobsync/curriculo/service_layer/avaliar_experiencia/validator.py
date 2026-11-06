"""Valida a entrada do caso de uso AvaliarExperiencia."""
from jobsync.curriculo.service_layer.avaliar_experiencia.dtos import (
    AvaliarExperienciaInputDto,
)


class AvaliarExperienciaInputValidator:
    @staticmethod
    def validar(input_dto: AvaliarExperienciaInputDto) -> None:
        if (
            not input_dto.experiencia.descricao
            or not input_dto.experiencia.descricao.strip()
        ):
            raise ValueError("O texto da experiência profissional é obrigatório.")
        if not input_dto.descricao_vaga or not input_dto.descricao_vaga.strip():
            raise ValueError("A descrição da vaga-alvo é obrigatória.")

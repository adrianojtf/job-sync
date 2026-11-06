"""Valida a entrada do caso de uso AvaliarDescricaoVaga."""
from jobsync.vaga.service_layer.avaliar_descricao_vaga.dtos import (
    AvaliarDescricaoVagaInputDto,
)


class AvaliarDescricaoVagaInputValidator:
    @staticmethod
    def validar(input_dto: AvaliarDescricaoVagaInputDto) -> None:
        if not input_dto.descricao_vaga or not input_dto.descricao_vaga.strip():
            raise ValueError("O texto da descrição da vaga é obrigatório.")

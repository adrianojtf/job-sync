"""Validator de input para o caso de uso AdaptarCurriculoParaVaga."""

from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AdaptarCurriculoParaVagaInputDto,
)
from jobsync.curriculo.service_layer.validacoes_vaga_alvo import (
    validar_cargo_e_empresa_alvo,
    validar_idioma_alvo,
)


class AdaptarCurriculoParaVagaInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: AdaptarCurriculoParaVagaInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        validar_idioma_alvo(input_dto.idioma_alvo)
        if not input_dto.descricao_vaga or not input_dto.descricao_vaga.strip():
            raise ValueError("A descrição da vaga é obrigatória.")
        if not input_dto.pdf_curriculo and input_dto.curriculo_pre_montado is None:
            raise ValueError("O PDF do currículo é obrigatório (ou informe curriculo_pre_montado).")
        validar_cargo_e_empresa_alvo(input_dto.cargo_alvo, input_dto.empresa_alvo)

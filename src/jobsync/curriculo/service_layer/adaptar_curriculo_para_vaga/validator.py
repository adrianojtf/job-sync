"""Validator de input para o caso de uso AdaptarCurriculoParaVaga."""

from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AdaptarCurriculoParaVagaInputDto,
)

IDIOMAS_SUPORTADOS = {"pt", "en"}


class AdaptarCurriculoParaVagaInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: AdaptarCurriculoParaVagaInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if input_dto.idioma_alvo not in IDIOMAS_SUPORTADOS:
            raise ValueError(
                f"idioma alvo inválido: '{input_dto.idioma_alvo}'. "
                f"Idiomas suportados: {sorted(IDIOMAS_SUPORTADOS)}"
            )
        if not input_dto.descricao_vaga or not input_dto.descricao_vaga.strip():
            raise ValueError("A descrição da vaga é obrigatória.")
        if not input_dto.pdf_curriculo and input_dto.curriculo_pre_montado is None:
            raise ValueError("O PDF do currículo é obrigatório (ou informe curriculo_pre_montado).")
        if not input_dto.cargo_alvo or not input_dto.cargo_alvo.strip():
            raise ValueError("O cargo alvo é obrigatório.")
        if not input_dto.empresa_alvo or not input_dto.empresa_alvo.strip():
            raise ValueError("A empresa alvo é obrigatória.")

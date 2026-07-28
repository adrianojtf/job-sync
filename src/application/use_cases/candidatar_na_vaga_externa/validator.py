"""Validator de input para o caso de uso CandidatarNaVagaExterna."""

from application.use_cases.candidatar_na_vaga_externa.dtos import CandidatarNaVagaExternaInputDto


class CandidatarNaVagaExternaInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: CandidatarNaVagaExternaInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if not input_dto.pdf_curriculo and input_dto.curriculo_pre_montado is None:
            raise ValueError("O PDF do currículo é obrigatório (ou informe curriculo_pre_montado).")
        if not input_dto.idioma_alvo or not input_dto.idioma_alvo.strip():
            raise ValueError("O idioma alvo é obrigatório.")
        if not input_dto.cargo_alvo or not input_dto.cargo_alvo.strip():
            raise ValueError("O cargo alvo é obrigatório.")
        if not input_dto.empresa_alvo or not input_dto.empresa_alvo.strip():
            raise ValueError("A empresa alvo é obrigatória.")

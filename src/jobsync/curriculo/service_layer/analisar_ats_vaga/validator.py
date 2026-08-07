"""Validator de input para o caso de uso AnalisarAtsVaga."""

from jobsync.curriculo.service_layer.analisar_ats_vaga.dtos import AnalisarAtsVagaInputDto


class AnalisarAtsVagaInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: AnalisarAtsVagaInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if not input_dto.pdf_curriculo and input_dto.curriculo_pre_montado is None:
            raise ValueError("O PDF do currículo é obrigatório (ou informe curriculo_pre_montado).")
        if not input_dto.descricao_vaga or not input_dto.descricao_vaga.strip():
            raise ValueError("A descrição da vaga é obrigatória.")

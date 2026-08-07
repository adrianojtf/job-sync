"""Validator de input para o caso de uso CriarCandidatura."""

from jobsync.candidatura.service_layer.criar_candidatura.dtos import CriarCandidaturaInputDto


class CriarCandidaturaInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: CriarCandidaturaInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if not input_dto.perfil_identificador or not input_dto.perfil_identificador.strip():
            raise ValueError("O identificador do perfil é obrigatório.")
        if not input_dto.vaga_id or not input_dto.vaga_id.strip():
            raise ValueError("A vaga de origem é obrigatória.")
        if not input_dto.curriculo_salvo_id or not input_dto.curriculo_salvo_id.strip():
            raise ValueError("O currículo salvo usado é obrigatório.")
        if not input_dto.empresa or not input_dto.empresa.strip():
            raise ValueError("A empresa da candidatura é obrigatória.")
        if not input_dto.cargo or not input_dto.cargo.strip():
            raise ValueError("O cargo da candidatura é obrigatório.")

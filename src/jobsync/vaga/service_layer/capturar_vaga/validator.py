"""Validator de input para o caso de uso CapturarVaga."""

from jobsync.vaga.service_layer.capturar_vaga.dtos import CapturarVagaInputDto


class CapturarVagaInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: CapturarVagaInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if not input_dto.perfil_identificador or not input_dto.perfil_identificador.strip():
            raise ValueError("O identificador do perfil é obrigatório.")
        if not input_dto.texto_descricao or not input_dto.texto_descricao.strip():
            raise ValueError("O texto da descrição da vaga é obrigatório.")

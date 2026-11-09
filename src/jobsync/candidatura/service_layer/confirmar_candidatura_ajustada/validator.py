"""Validator de input para o caso de uso ConfirmarCandidaturaAjustada."""

from jobsync.candidatura.service_layer.confirmar_candidatura_ajustada.dtos import (
    ConfirmarCandidaturaAjustadaInputDto,
)

_ASSINATURA_DE_PDF = b"%PDF"


class ConfirmarCandidaturaAjustadaInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: ConfirmarCandidaturaAjustadaInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if not input_dto.perfil_identificador or not input_dto.perfil_identificador.strip():
            raise ValueError("O identificador do perfil é obrigatório.")
        if not input_dto.cargo or not input_dto.cargo.strip():
            raise ValueError("O cargo da vaga é obrigatório.")
        if not input_dto.empresa or not input_dto.empresa.strip():
            raise ValueError("A empresa da candidatura é obrigatória.")
        if not input_dto.descricao_vaga or not input_dto.descricao_vaga.strip():
            raise ValueError("A descrição da vaga é obrigatória.")
        if not input_dto.nome_arquivo or not input_dto.nome_arquivo.strip():
            raise ValueError("O nome do arquivo do currículo é obrigatório.")
        if not input_dto.pdf_bytes:
            raise ValueError("O PDF do currículo é obrigatório.")
        if not input_dto.pdf_bytes.startswith(_ASSINATURA_DE_PDF):
            raise ValueError("O arquivo enviado não é um PDF válido.")

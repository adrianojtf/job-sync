"""Validator de input para o caso de uso ImportarPerfilDePdf."""

from jobsync.perfil_estruturado.service_layer.importar_perfil_de_pdf.dtos import ImportarPerfilDePdfInputDto


class ImportarPerfilDePdfInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: ImportarPerfilDePdfInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if not input_dto.pdf_curriculo:
            raise ValueError("O PDF do currículo é obrigatório.")

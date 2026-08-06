"""Validator de input para o caso de uso SalvarCurriculo."""

from jobsync.curriculo_salvo.service_layer.salvar_curriculo.dtos import SalvarCurriculoInputDto


class SalvarCurriculoInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: SalvarCurriculoInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if not input_dto.perfil_identificador or not input_dto.perfil_identificador.strip():
            raise ValueError("O identificador do perfil é obrigatório.")
        if not input_dto.nome_referencia or not input_dto.nome_referencia.strip():
            raise ValueError("O nome de referência do currículo é obrigatório.")
        if not input_dto.pdf_bytes:
            raise ValueError("O conteúdo do PDF do currículo é obrigatório.")

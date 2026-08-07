"""Validator de input para o caso de uso SalvarPerfilEstruturado."""

from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado.dtos import SalvarPerfilEstruturadoInputDto


class SalvarPerfilEstruturadoInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: SalvarPerfilEstruturadoInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if not input_dto.perfil_identificador or not input_dto.perfil_identificador.strip():
            raise ValueError("O identificador do perfil é obrigatório.")
        if not input_dto.nome_completo or not input_dto.nome_completo.strip():
            raise ValueError("O nome completo é obrigatório.")
        if not input_dto.email or not input_dto.email.strip():
            raise ValueError("O email é obrigatório.")

"""Validator de input para o caso de uso VerificarConquistasParecidas."""

from jobsync.perfil_estruturado.service_layer.verificar_conquistas_parecidas.dtos import (
    VerificarConquistasParecidasInputDto,
)


class VerificarConquistasParecidasInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: VerificarConquistasParecidasInputDto) -> None:
        """Levanta ValueError se o texto da conquista for vazio."""
        if not input_dto.texto or not input_dto.texto.strip():
            raise ValueError("O texto da conquista é obrigatório.")

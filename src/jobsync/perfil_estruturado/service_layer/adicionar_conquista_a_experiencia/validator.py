"""Validator de input para o caso de uso AdicionarConquistaAExperiencia."""

from jobsync.perfil_estruturado.service_layer.adicionar_conquista_a_experiencia.dtos import (
    AdicionarConquistaAExperienciaInputDto,
)


class AdicionarConquistaAExperienciaInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: AdicionarConquistaAExperienciaInputDto) -> None:
        """Levanta ValueError se o texto da conquista for vazio."""
        if not input_dto.texto or not input_dto.texto.strip():
            raise ValueError("O texto da conquista não pode ser vazio.")

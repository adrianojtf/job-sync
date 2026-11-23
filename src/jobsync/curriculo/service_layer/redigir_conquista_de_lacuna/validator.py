"""Validator de input para o caso de uso RedigirConquistaDeLacuna."""

from jobsync.curriculo.service_layer.redigir_conquista_de_lacuna.dtos import RedigirConquistaDeLacunaInputDto
from jobsync.curriculo.service_layer.validacoes_vaga_alvo import validar_idioma_alvo


class RedigirConquistaDeLacunaInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: RedigirConquistaDeLacunaInputDto) -> None:
        """Levanta ValueError se o caso estiver vazio ou o idioma não for suportado."""
        if not input_dto.caso or not input_dto.caso.strip():
            raise ValueError("O caso descrito pelo candidato é obrigatório.")
        validar_idioma_alvo(input_dto.idioma_alvo)

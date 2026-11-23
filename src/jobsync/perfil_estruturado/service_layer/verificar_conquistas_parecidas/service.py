"""Caso de uso: avisar quais conquistas já guardadas se parecem com uma conquista nova (JOB-0042)."""
from __future__ import annotations

from jobsync.perfil_estruturado.domain.conquistas_parecidas import sao_parecidas
from jobsync.perfil_estruturado.service_layer.verificar_conquistas_parecidas.dtos import (
    VerificarConquistasParecidasInputDto,
)
from jobsync.perfil_estruturado.service_layer.verificar_conquistas_parecidas.validator import (
    VerificarConquistasParecidasInputValidator,
)


class VerificarConquistasParecidas:
    """Compara o texto novo com as conquistas informadas, sem consultar o banco."""

    def executar(self, input_dto: VerificarConquistasParecidasInputDto) -> tuple[str, ...]:
        VerificarConquistasParecidasInputValidator.validar(input_dto)
        return tuple(
            conquista for conquista in input_dto.conquistas if sao_parecidas(conquista, input_dto.texto)
        )

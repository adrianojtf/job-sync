"""Caso de uso: redigir, via IA, a conquista que nasce da resposta a uma lacuna (JOB-0043).

Nada é persistido aqui: o candidato revisa o texto e só a conquista aprovada é salva no banco.
"""
from __future__ import annotations

from dataclasses import replace

from jobsync.curriculo.domain.redator_conquista_port import RedatorConquistaPort
from jobsync.curriculo.service_layer.redigir_conquista_de_lacuna.dtos import RedigirConquistaDeLacunaInputDto
from jobsync.curriculo.service_layer.redigir_conquista_de_lacuna.validator import (
    RedigirConquistaDeLacunaInputValidator,
)
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel


class RedigirConquistaDeLacuna:
    """Pede a redação à porta de IA; falha da IA vira `SugestaoIAIndisponivel` (502 na API)."""

    def __init__(self, redator: RedatorConquistaPort) -> None:
        self._redator = redator

    def executar(self, input_dto: RedigirConquistaDeLacunaInputDto) -> str:
        RedigirConquistaDeLacunaInputValidator.validar(input_dto)
        entrada = replace(input_dto, caso=input_dto.caso.strip())
        try:
            return self._redator.redigir(
                entrada.lacuna, entrada.caso, entrada.cargo, entrada.idioma_alvo
            )
        except (RuntimeError, ValueError) as erro:
            raise SugestaoIAIndisponivel() from erro

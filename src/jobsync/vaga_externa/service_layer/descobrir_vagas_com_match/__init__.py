"""Caso de uso: descobrir vagas em fontes externas com match calculado."""

from jobsync.vaga_externa.service_layer.descobrir_vagas_com_match.service import (
    DescobrirVagasComMatch,
    LIMITE_VAGAS_ANALISADAS,
)

__all__ = ["DescobrirVagasComMatch", "LIMITE_VAGAS_ANALISADAS"]

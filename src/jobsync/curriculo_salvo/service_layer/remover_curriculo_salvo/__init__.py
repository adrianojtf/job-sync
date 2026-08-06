"""Caso de uso: remover currículo salvo."""

from jobsync.curriculo_salvo.service_layer.remover_curriculo_salvo.service import (
    CurriculoSalvoNaoEncontrado,
    RemoverCurriculoSalvo,
)

__all__ = ["RemoverCurriculoSalvo", "CurriculoSalvoNaoEncontrado"]

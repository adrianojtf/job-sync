"""Limitador de leituras de vaga por pessoa, mantido em memória.

O controle vale por processo: é reiniciado junto com ele e, com vários
processos, o limite efetivo é multiplicado pelo número deles.
"""
from __future__ import annotations

import math
import threading
import time
from collections import deque
from typing import Callable

from jobsync.vaga.domain.exceptions import LimiteLeituraVagaExcedido
from jobsync.vaga.domain.limitador_leitura_vaga_port import LimitadorLeituraVagaPort

_SEGUNDOS_POR_MINUTO = 60
_SEGUNDOS_POR_DIA = 86_400


class LimitadorLeituraVagaEmMemoria(LimitadorLeituraVagaPort):
    """Janela deslizante por usuário, com limites por minuto e por dia."""

    def __init__(
        self,
        limite_por_minuto: int = 10,
        limite_por_dia: int = 100,
        relogio: Callable[[], float] = time.time,
    ) -> None:
        if limite_por_minuto < 1 or limite_por_dia < 1:
            raise ValueError("Os limites de leitura de vaga devem ser maiores que zero.")
        self._limite_por_minuto = limite_por_minuto
        self._limite_por_dia = limite_por_dia
        self._relogio = relogio
        self._leituras: dict[str, deque[float]] = {}
        self._trava = threading.Lock()

    def registrar(self, usuario_id: str) -> None:
        with self._trava:
            agora = self._relogio()
            leituras = self._leituras.setdefault(usuario_id, deque())
            while leituras and agora - leituras[0] >= _SEGUNDOS_POR_DIA:
                leituras.popleft()

            espera = max(
                self._espera(leituras, agora, _SEGUNDOS_POR_MINUTO, self._limite_por_minuto),
                self._espera(leituras, agora, _SEGUNDOS_POR_DIA, self._limite_por_dia),
            )
            if espera > 0:
                raise LimiteLeituraVagaExcedido(max(1, math.ceil(espera)))
            leituras.append(agora)

    @staticmethod
    def _espera(leituras: deque[float], agora: float, janela: int, limite: int) -> float:
        recentes = [momento for momento in leituras if agora - momento < janela]
        if len(recentes) < limite:
            return 0.0
        return recentes[-limite] + janela - agora

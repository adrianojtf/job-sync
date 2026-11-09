"""Validações e registro comuns aos casos de uso de sugestão de IA."""
from __future__ import annotations

import logging
from time import perf_counter

from jobsync.curriculo.domain.refino import FocoRefino, PedidoRefino

LIMITE_CARACTERES_SUGESTAO = 5000

logger = logging.getLogger(__name__)


def validar_tamanho_do_texto(texto: str) -> None:
    """Limita o texto enviado à IA, para conter custo e latência."""
    if len(texto) > LIMITE_CARACTERES_SUGESTAO:
        raise ValueError(
            f"O texto excede o limite de {LIMITE_CARACTERES_SUGESTAO} caracteres para sugestões."
        )


def validar_refino(refino: PedidoRefino) -> None:
    """As sugestões anteriores também vão para a IA, então seguem o mesmo limite."""
    for sugestao in refino.sugestoes_anteriores:
        validar_tamanho_do_texto(sugestao)


def registrar_sugestao(
    modo: str,
    tipo: str,
    tamanho_entrada: int,
    tamanho_saida: int,
    inicio: float,
    refino: PedidoRefino,
    foco: FocoRefino,
) -> None:
    """Registra a sugestão sem conteúdo do currículo: modo, tipo, tamanhos, duração, tentativa e foco."""
    logger.info(
        "Sugestão de IA gerada (modo=%s, tipo=%s, entrada=%d, saida=%d, duracao_ms=%d, tentativa=%d, foco=%s).",
        modo,
        tipo,
        tamanho_entrada,
        tamanho_saida,
        int((perf_counter() - inicio) * 1000),
        refino.tentativa,
        foco.value,
    )

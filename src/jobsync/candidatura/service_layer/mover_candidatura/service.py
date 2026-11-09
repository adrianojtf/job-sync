"""Caso de uso: mover uma candidatura entre colunas do Kanban ou reordená-la na coluna.

Aceita qualquer transição entre os quatro status (sem máquina de estados
restritiva), conforme decidido em produto.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from jobsync.candidatura.domain.candidatura import Candidatura, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import (
    CandidaturaNaoEncontrada,
    CandidaturaRepository,
)
from jobsync.candidatura.domain.ordenacao_coluna import reposicionar

logger = logging.getLogger(__name__)


@dataclass
class MoverCandidatura:
    """Atualiza o status e a posição de uma candidatura na coluna de destino."""

    repositorio_candidatura: CandidaturaRepository

    def executar(
        self,
        candidatura_id: str,
        novo_status: StatusCandidatura,
        posicao: int | None = None,
    ) -> Candidatura:
        atual = self.repositorio_candidatura.buscar_por_id(candidatura_id)
        if atual is None:
            raise CandidaturaNaoEncontrada(candidatura_id)

        ids_destino = tuple(
            c.id
            for c in self.repositorio_candidatura.listar_por_perfil(atual.perfil_identificador)
            if c.status == novo_status and c.id != candidatura_id
        )
        nova_ordem = reposicionar(ids_destino, candidatura_id, posicao)
        if posicao is not None and posicao > len(ids_destino):
            logger.warning(
                "Posição %s limitada ao fim da coluna %s (candidatura %s).",
                posicao,
                novo_status.name,
                candidatura_id,
            )

        movida = self.repositorio_candidatura.aplicar_movimento(candidatura_id, novo_status, nova_ordem)
        logger.info(
            "Candidatura %s movida de %s para %s na posição %s.",
            candidatura_id,
            atual.status.name,
            novo_status.name,
            movida.posicao,
        )
        return movida

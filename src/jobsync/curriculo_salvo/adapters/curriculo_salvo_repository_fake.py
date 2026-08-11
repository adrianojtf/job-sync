"""Implementação em memória (fake) de CurriculoSalvoRepository para testes."""

from __future__ import annotations

from jobsync.curriculo_salvo.domain.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.domain.curriculo_salvo_repository import (
    CurriculoSalvoRepository,
)


class CurriculoSalvoRepositoryFake(CurriculoSalvoRepository):
    """Fake em memória para testes de API e serviços."""

    def __init__(self) -> None:
        self._curriculos: dict[str, CurriculoSalvo] = {}

    def salvar(self, curriculo: CurriculoSalvo) -> CurriculoSalvo:
        self._curriculos[curriculo.id] = curriculo
        return curriculo

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        itens = [
            c
            for c in self._curriculos.values()
            if c.perfil_identificador == perfil_identificador
        ]
        itens.sort(key=lambda c: c.data_upload, reverse=True)
        return tuple(itens)

    def remover(self, curriculo_id: str, perfil_identificador: str) -> None:
        curriculo = self._curriculos.get(curriculo_id)
        if curriculo and curriculo.perfil_identificador == perfil_identificador:
            del self._curriculos[curriculo_id]

    def contar_por_perfil(self, perfil_identificador: str) -> int:
        return sum(
            1
            for c in self._curriculos.values()
            if c.perfil_identificador == perfil_identificador
        )

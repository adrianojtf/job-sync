"""Implementação em memória (fake) de CurriculoAdaptadoRepository para testes."""
from __future__ import annotations

from dataclasses import replace

from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.curriculo_adaptado.domain.curriculo_adaptado_repository import (
    CurriculoAdaptadoRepository,
)


class CurriculoAdaptadoRepositoryFake(CurriculoAdaptadoRepository):
    def __init__(self) -> None:
        self._curriculos: dict[str, CurriculoAdaptado] = {}

    def salvar(self, curriculo: CurriculoAdaptado) -> CurriculoAdaptado:
        self._curriculos[curriculo.id] = curriculo
        return curriculo

    def buscar(self, curriculo_id: str, perfil_identificador: str) -> CurriculoAdaptado | None:
        curriculo = self._curriculos.get(curriculo_id)
        if curriculo is None or curriculo.perfil_identificador != perfil_identificador:
            return None
        return curriculo

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoAdaptado, ...]:
        itens = [c for c in self._curriculos.values() if c.perfil_identificador == perfil_identificador]
        itens.sort(key=lambda c: (c.atualizado_em, c.id), reverse=True)
        return tuple(itens)

    def vincular_curriculo_salvo(
        self, curriculo_id: str, perfil_identificador: str, curriculo_salvo_id: str
    ) -> None:
        curriculo = self.buscar(curriculo_id, perfil_identificador)
        if curriculo is not None:
            self._curriculos[curriculo_id] = replace(curriculo, curriculo_salvo_id=curriculo_salvo_id)

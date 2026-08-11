"""Implementação em memória (fake) de VagaRepository para testes."""

from __future__ import annotations

from jobsync.vaga.domain.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository


class VagaRepositoryFake(VagaRepository):
    """Fake em memória para testes de API e serviços."""

    def __init__(self) -> None:
        self._vagas: dict[str, Vaga] = {}
        self._convertidas: set[str] = set()

    def salvar(self, vaga: Vaga) -> Vaga:
        self._vagas[vaga.id] = vaga
        return vaga

    def listar_nao_convertidas(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        itens = [
            v
            for v in self._vagas.values()
            if v.perfil_identificador == perfil_identificador
            and v.id not in self._convertidas
        ]
        itens.sort(key=lambda v: v.data_captura, reverse=True)
        return tuple(itens)

    def marcar_como_convertida(self, vaga_id: str) -> None:
        if vaga_id not in self._vagas:
            raise ValueError("Vaga não encontrada.")
        self._convertidas.add(vaga_id)

"""Testes do caso de uso RemoverCurriculoSalvo."""
from datetime import datetime

import pytest

from jobsync.curriculo_salvo import CurriculoSalvo, CurriculoSalvoRepository
from jobsync.curriculo_salvo.service_layer.remover_curriculo_salvo import (
    CurriculoSalvoNaoEncontrado,
    RemoverCurriculoSalvo,
)


class CurriculoSalvoRepositoryFake(CurriculoSalvoRepository):
    def __init__(self, curriculos: tuple[CurriculoSalvo, ...]):
        self._curriculos = list(curriculos)
        self.chamou_remover_com: tuple[str, str] | None = None

    def salvar(self, curriculo: CurriculoSalvo) -> CurriculoSalvo:
        raise NotImplementedError

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        return tuple(c for c in self._curriculos if c.perfil_identificador == perfil_identificador)

    def remover(self, curriculo_id: str, perfil_identificador: str) -> None:
        self.chamou_remover_com = (curriculo_id, perfil_identificador)
        self._curriculos = [c for c in self._curriculos if c.id != curriculo_id]

    def contar_por_perfil(self, perfil_identificador: str) -> int:
        raise NotImplementedError

    def atualizar_pdf(self, curriculo_id: str, perfil_identificador: str, pdf_bytes: bytes) -> bool:
        return False



def _criar_curriculo_salvo(**overrides) -> CurriculoSalvo:
    dados = dict(
        id="uuid-1",
        perfil_identificador="matheus",
        nome_referencia="Currículo Backend",
        pdf_bytes=b"%PDF-fake",
        data_upload=datetime(2026, 7, 26),
    )
    dados.update(overrides)
    return CurriculoSalvo(**dados)


class TestRemoverCurriculoSalvo:
    def test_remove_curriculo_pertencente_ao_perfil(self):
        curriculo = _criar_curriculo_salvo(id="uuid-matheus", perfil_identificador="matheus")
        repositorio = CurriculoSalvoRepositoryFake(curriculos=(curriculo,))
        use_case = RemoverCurriculoSalvo(repositorio)

        use_case.executar("uuid-matheus", "matheus")

        assert repositorio.chamou_remover_com == ("uuid-matheus", "matheus")

    def test_rejeita_remocao_de_curriculo_de_outro_perfil(self):
        curriculo_outra_pessoa = _criar_curriculo_salvo(id="uuid-outra", perfil_identificador="outra-pessoa")
        repositorio = CurriculoSalvoRepositoryFake(curriculos=(curriculo_outra_pessoa,))
        use_case = RemoverCurriculoSalvo(repositorio)

        with pytest.raises(CurriculoSalvoNaoEncontrado):
            use_case.executar("uuid-outra", "matheus")

        assert repositorio.chamou_remover_com is None

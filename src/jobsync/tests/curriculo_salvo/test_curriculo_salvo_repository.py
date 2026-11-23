"""Testes de porta para o repositório de currículos salvos."""

from datetime import datetime

from jobsync.curriculo_salvo import CurriculoSalvo, CurriculoSalvoRepository


class CurriculoSalvoRepositoryFake(CurriculoSalvoRepository):
    def __init__(self) -> None:
        self._curriculos: list[CurriculoSalvo] = []

    def salvar(self, curriculo: CurriculoSalvo) -> CurriculoSalvo:
        self._curriculos.append(curriculo)
        return curriculo

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        encontrados = [c for c in self._curriculos if c.perfil_identificador == perfil_identificador]
        return tuple(sorted(encontrados, key=lambda c: c.data_upload, reverse=True))

    def remover(self, curriculo_id: str, perfil_identificador: str) -> None:
        self._curriculos = [
            c
            for c in self._curriculos
            if not (c.id == curriculo_id and c.perfil_identificador == perfil_identificador)
        ]

    def contar_por_perfil(self, perfil_identificador: str) -> int:
        return len(self.listar_por_perfil(perfil_identificador))

    def atualizar_pdf(self, curriculo_id: str, perfil_identificador: str, pdf_bytes: bytes) -> bool:
        return False



def _criar_curriculo_salvo(**overrides) -> CurriculoSalvo:
    dados = dict(
        id="uuid-1",
        perfil_identificador="matheus",
        nome_referencia="Currículo Backend",
        pdf_bytes=b"%PDF-fake",
        data_upload=datetime(2026, 7, 26, 12, 0, 0),
    )
    dados.update(overrides)
    return CurriculoSalvo(**dados)


def test_curriculo_salvo_repository_eh_interface_pura() -> None:
    fake = CurriculoSalvoRepositoryFake()
    curriculo = _criar_curriculo_salvo()

    fake.salvar(curriculo)

    assert fake.contar_por_perfil("matheus") == 1
    assert fake.listar_por_perfil("matheus") == (curriculo,)

    fake.remover(curriculo.id, "matheus")

    assert fake.contar_por_perfil("matheus") == 0

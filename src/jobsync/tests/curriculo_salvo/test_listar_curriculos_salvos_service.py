"""Testes do caso de uso ListarCurriculosSalvos."""
from datetime import datetime

from jobsync.curriculo_salvo import CurriculoSalvo, CurriculoSalvoRepository
from jobsync.curriculo_salvo.service_layer.listar_curriculos_salvos import ListarCurriculosSalvos


class CurriculoSalvoRepositoryFake(CurriculoSalvoRepository):
    def __init__(self, curriculos: tuple[CurriculoSalvo, ...]):
        self._curriculos = curriculos

    def salvar(self, curriculo: CurriculoSalvo) -> CurriculoSalvo:
        raise NotImplementedError

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        return tuple(c for c in self._curriculos if c.perfil_identificador == perfil_identificador)

    def remover(self, curriculo_id: str, perfil_identificador: str) -> None:
        raise NotImplementedError

    def contar_por_perfil(self, perfil_identificador: str) -> int:
        raise NotImplementedError


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


class TestListarCurriculosSalvos:
    def test_lista_apenas_curriculos_do_perfil_informado(self):
        curriculo_matheus = _criar_curriculo_salvo(id="uuid-matheus", perfil_identificador="matheus")
        curriculo_outra_pessoa = _criar_curriculo_salvo(id="uuid-outra", perfil_identificador="outra-pessoa")
        repositorio = CurriculoSalvoRepositoryFake(curriculos=(curriculo_matheus, curriculo_outra_pessoa))
        use_case = ListarCurriculosSalvos(repositorio)

        resultado = use_case.executar("matheus")

        assert resultado == (curriculo_matheus,)

    def test_lista_vazia_quando_perfil_sem_curriculos(self):
        repositorio = CurriculoSalvoRepositoryFake(curriculos=())
        use_case = ListarCurriculosSalvos(repositorio)

        resultado = use_case.executar("matheus")

        assert resultado == ()

"""Testes do caso de uso SalvarCurriculo."""
from datetime import datetime

import pytest

from jobsync.curriculo_salvo import CurriculoSalvo, CurriculoSalvoRepository
from jobsync.curriculo_salvo.service_layer.salvar_curriculo import (
    LIMITE_CURRICULOS_POR_PERFIL,
    LimiteCurriculosSalvosExcedido,
    SalvarCurriculo,
    SalvarCurriculoInputDto,
)


class CurriculoSalvoRepositoryFake(CurriculoSalvoRepository):
    def __init__(self, quantidade_inicial: int = 0):
        self._curriculos: list[CurriculoSalvo] = []
        self._quantidade_inicial = quantidade_inicial
        self.chamou_salvar = False

    def salvar(self, curriculo: CurriculoSalvo) -> CurriculoSalvo:
        self.chamou_salvar = True
        self._curriculos.append(curriculo)
        return curriculo

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        return tuple(self._curriculos)

    def remover(self, curriculo_id: str, perfil_identificador: str) -> None:
        raise NotImplementedError

    def contar_por_perfil(self, perfil_identificador: str) -> int:
        return self._quantidade_inicial + len(self._curriculos)


class TestSalvarCurriculo:
    def test_salva_curriculo_quando_abaixo_do_limite(self):
        repositorio = CurriculoSalvoRepositoryFake(quantidade_inicial=3)
        use_case = SalvarCurriculo(repositorio)

        resultado = use_case.executar(
            SalvarCurriculoInputDto(
                perfil_identificador="matheus",
                nome_referencia="Currículo Backend",
                pdf_bytes=b"%PDF-fake",
            )
        )

        assert repositorio.chamou_salvar is True
        assert resultado.perfil_identificador == "matheus"
        assert resultado.nome_referencia == "Currículo Backend"
        assert isinstance(resultado.data_upload, datetime)

    def test_bloqueia_salvamento_quando_no_limite(self):
        repositorio = CurriculoSalvoRepositoryFake(quantidade_inicial=LIMITE_CURRICULOS_POR_PERFIL)
        use_case = SalvarCurriculo(repositorio)

        with pytest.raises(LimiteCurriculosSalvosExcedido):
            use_case.executar(
                SalvarCurriculoInputDto(
                    perfil_identificador="matheus",
                    nome_referencia="11º currículo",
                    pdf_bytes=b"%PDF-fake",
                )
            )

        assert repositorio.chamou_salvar is False

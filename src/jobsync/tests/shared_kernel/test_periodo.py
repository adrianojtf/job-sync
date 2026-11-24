import json
from pathlib import Path

import pytest

from jobsync.shared_kernel.domain.periodo import Periodo, PeriodoInvalido, validar_ano

CASOS = json.loads(
    (Path(__file__).resolve().parents[4] / "frontend/src/shared/formulario-curriculo/periodo.casos.json").read_text(
        encoding="utf-8"
    )
)
PERIODOS_VALIDOS = [c for c in CASOS["periodos"] if c["valido"]]
PERIODOS_INVALIDOS = [c for c in CASOS["periodos"] if not c["valido"]]


class TestPeriodo:
    @pytest.mark.parametrize("caso", PERIODOS_VALIDOS, ids=lambda c: c["texto"])
    def test_le_o_inicio_e_o_fim_da_tabela_compartilhada(self, caso):
        periodo = Periodo.ler(caso["texto"])

        assert periodo.inicio == tuple(caso["inicio"])
        assert periodo.fim == (None if caso["fim"] is None else tuple(caso["fim"]))
        assert periodo.atual is (caso["fim"] is None)

    @pytest.mark.parametrize("caso", PERIODOS_INVALIDOS, ids=lambda c: c["texto"])
    def test_recusa_os_periodos_invalidos_da_tabela_compartilhada(self, caso):
        with pytest.raises(PeriodoInvalido):
            Periodo.ler(caso["texto"])

    def test_a_mensagem_de_erro_traz_exemplos_do_formato(self):
        with pytest.raises(PeriodoInvalido) as erro:
            Periodo.ler("ontem")

        assert "Mar 2024 - Atual" in str(erro.value)
        assert "2020 - 2022" in str(erro.value)

    def test_periodo_invalido_e_um_value_error(self):
        assert issubclass(PeriodoInvalido, ValueError)

    def test_ano_inicial_e_o_ano_do_inicio(self):
        assert Periodo.ler("Mar 2026 - Atual").ano_inicial == 2026


class TestValidarAno:
    @pytest.mark.parametrize("caso", CASOS["anos"], ids=lambda c: c["texto"])
    def test_tabela_compartilhada_de_anos(self, caso):
        if caso["valido"]:
            validar_ano(caso["texto"])
        else:
            with pytest.raises(PeriodoInvalido):
                validar_ano(caso["texto"])

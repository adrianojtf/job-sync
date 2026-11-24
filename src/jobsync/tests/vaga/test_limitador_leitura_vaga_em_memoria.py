import threading

import pytest

from jobsync.vaga import LimiteLeituraVagaExcedido
from jobsync.vaga.adapters import LimitadorLeituraVagaEmMemoria


class RelogioFake:
    def __init__(self, agora: float = 1_000.0):
        self.agora = agora

    def __call__(self) -> float:
        return self.agora

    def avancar(self, segundos: float) -> None:
        self.agora += segundos


class TestLimitadorLeituraVagaEmMemoria:
    def test_permite_leituras_ate_o_limite_por_minuto(self):
        relogio = RelogioFake()
        limitador = LimitadorLeituraVagaEmMemoria(limite_por_minuto=3, limite_por_dia=100, relogio=relogio)

        for _ in range(3):
            limitador.registrar("usuario-1")

    def test_bloqueia_a_leitura_acima_do_limite_por_minuto_e_informa_a_espera(self):
        relogio = RelogioFake()
        limitador = LimitadorLeituraVagaEmMemoria(limite_por_minuto=2, limite_por_dia=100, relogio=relogio)
        limitador.registrar("usuario-1")
        relogio.avancar(10)
        limitador.registrar("usuario-1")
        relogio.avancar(20)

        with pytest.raises(LimiteLeituraVagaExcedido) as erro:
            limitador.registrar("usuario-1")

        assert erro.value.segundos_para_nova_tentativa == 30

    def test_libera_novamente_depois_de_um_minuto(self):
        relogio = RelogioFake()
        limitador = LimitadorLeituraVagaEmMemoria(limite_por_minuto=1, limite_por_dia=100, relogio=relogio)
        limitador.registrar("usuario-1")
        relogio.avancar(61)

        limitador.registrar("usuario-1")

    def test_bloqueia_acima_do_limite_por_dia(self):
        relogio = RelogioFake()
        limitador = LimitadorLeituraVagaEmMemoria(limite_por_minuto=1000, limite_por_dia=3, relogio=relogio)
        for _ in range(3):
            limitador.registrar("usuario-1")
            relogio.avancar(3600)

        with pytest.raises(LimiteLeituraVagaExcedido) as erro:
            limitador.registrar("usuario-1")

        assert erro.value.segundos_para_nova_tentativa == 86_400 - 3 * 3600

    def test_libera_novamente_depois_de_um_dia(self):
        relogio = RelogioFake()
        limitador = LimitadorLeituraVagaEmMemoria(limite_por_minuto=1000, limite_por_dia=1, relogio=relogio)
        limitador.registrar("usuario-1")
        relogio.avancar(86_401)

        limitador.registrar("usuario-1")

    def test_leitura_recusada_nao_consome_o_limite(self):
        relogio = RelogioFake()
        limitador = LimitadorLeituraVagaEmMemoria(limite_por_minuto=1, limite_por_dia=100, relogio=relogio)
        limitador.registrar("usuario-1")
        for _ in range(5):
            with pytest.raises(LimiteLeituraVagaExcedido):
                limitador.registrar("usuario-1")
        relogio.avancar(61)

        limitador.registrar("usuario-1")

        with pytest.raises(LimiteLeituraVagaExcedido):
            limitador.registrar("usuario-1")

    def test_isola_o_limite_entre_usuarios(self):
        relogio = RelogioFake()
        limitador = LimitadorLeituraVagaEmMemoria(limite_por_minuto=1, limite_por_dia=100, relogio=relogio)
        limitador.registrar("usuario-1")

        limitador.registrar("usuario-2")

        with pytest.raises(LimiteLeituraVagaExcedido):
            limitador.registrar("usuario-1")

    def test_informa_ao_menos_um_segundo_de_espera(self):
        relogio = RelogioFake()
        limitador = LimitadorLeituraVagaEmMemoria(limite_por_minuto=1, limite_por_dia=100, relogio=relogio)
        limitador.registrar("usuario-1")
        relogio.avancar(59.9)

        with pytest.raises(LimiteLeituraVagaExcedido) as erro:
            limitador.registrar("usuario-1")

        assert erro.value.segundos_para_nova_tentativa == 1

    def test_respeita_o_limite_com_leituras_simultaneas(self):
        limitador = LimitadorLeituraVagaEmMemoria(limite_por_minuto=10, limite_por_dia=100)
        aceitas: list[int] = []
        recusadas: list[int] = []

        def registrar(indice: int) -> None:
            try:
                limitador.registrar("usuario-1")
                aceitas.append(indice)
            except LimiteLeituraVagaExcedido:
                recusadas.append(indice)

        threads = [threading.Thread(target=registrar, args=(i,)) for i in range(40)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(aceitas) == 10
        assert len(recusadas) == 30

    @pytest.mark.parametrize("por_minuto, por_dia", [(0, 10), (10, 0), (-1, 10)])
    def test_recusa_limites_invalidos(self, por_minuto, por_dia):
        with pytest.raises(ValueError):
            LimitadorLeituraVagaEmMemoria(limite_por_minuto=por_minuto, limite_por_dia=por_dia)

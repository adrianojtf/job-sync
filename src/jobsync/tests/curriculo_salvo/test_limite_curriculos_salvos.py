import pytest

from jobsync.curriculo_salvo.domain.limite_curriculos_salvos import (
    LIMITE_CURRICULOS_POR_PERFIL,
    LimiteCurriculosSalvosExcedido,
    garantir_espaco,
)


class TestGarantirEspaco:
    def test_limite_e_de_dez_curriculos_por_perfil(self):
        assert LIMITE_CURRICULOS_POR_PERFIL == 10

    @pytest.mark.parametrize("quantidade_atual", [0, 1, 9])
    def test_nao_levanta_quando_ainda_ha_espaco_na_biblioteca(self, quantidade_atual):
        garantir_espaco(quantidade_atual)

    @pytest.mark.parametrize("quantidade_atual", [10, 11])
    def test_levanta_quando_a_biblioteca_ja_atingiu_o_limite(self, quantidade_atual):
        with pytest.raises(LimiteCurriculosSalvosExcedido):
            garantir_espaco(quantidade_atual)

    def test_mensagem_orienta_a_remover_um_curriculo(self):
        with pytest.raises(LimiteCurriculosSalvosExcedido) as erro:
            garantir_espaco(LIMITE_CURRICULOS_POR_PERFIL)

        assert str(erro.value) == (
            "Limite de 10 currículos salvos atingido. "
            "Remova um currículo existente antes de salvar um novo."
        )

    def test_excecao_continua_sendo_value_error(self):
        assert issubclass(LimiteCurriculosSalvosExcedido, ValueError)


class TestReexportacaoDoCasoDeUso:
    def test_service_layer_exporta_os_mesmos_objetos_do_dominio(self):
        from jobsync.curriculo_salvo.service_layer import salvar_curriculo

        assert salvar_curriculo.LimiteCurriculosSalvosExcedido is LimiteCurriculosSalvosExcedido
        assert salvar_curriculo.LIMITE_CURRICULOS_POR_PERFIL == LIMITE_CURRICULOS_POR_PERFIL

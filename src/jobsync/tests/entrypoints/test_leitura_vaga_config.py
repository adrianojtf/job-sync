import pytest

from jobsync.entrypoints.leitura_vaga_config import (
    ConfiguracaoLeituraVaga,
    configuracao_leitura_vaga_do_ambiente,
)


class TestConfiguracaoLeituraVagaDoAmbiente:
    def test_usa_os_valores_padrao_quando_o_ambiente_esta_vazio(self):
        configuracao = configuracao_leitura_vaga_do_ambiente({})

        assert configuracao == ConfiguracaoLeituraVaga(
            linkedin_habilitado=True,
            limite_por_minuto=10,
            limite_por_dia=100,
            timeout_segundos=15.0,
        )

    def test_le_os_valores_informados(self):
        configuracao = configuracao_leitura_vaga_do_ambiente(
            {
                "VAGA_LEITURA_LINKEDIN_HABILITADA": "false",
                "VAGA_LEITURA_LIMITE_POR_MINUTO": "3",
                "VAGA_LEITURA_LIMITE_POR_DIA": "20",
                "VAGA_LEITURA_TIMEOUT_SEGUNDOS": "7.5",
            }
        )

        assert configuracao.linkedin_habilitado is False
        assert configuracao.limite_por_minuto == 3
        assert configuracao.limite_por_dia == 20
        assert configuracao.timeout_segundos == 7.5

    @pytest.mark.parametrize("valor", ["false", "FALSE", "0", "no", "off", " False "])
    def test_interpreta_valores_falsos_para_desligar_o_linkedin(self, valor):
        configuracao = configuracao_leitura_vaga_do_ambiente({"VAGA_LEITURA_LINKEDIN_HABILITADA": valor})

        assert configuracao.linkedin_habilitado is False

    @pytest.mark.parametrize("valor", ["true", "1", "yes", "on", "", "qualquer coisa"])
    def test_mantem_o_linkedin_ligado_para_os_demais_valores(self, valor):
        configuracao = configuracao_leitura_vaga_do_ambiente({"VAGA_LEITURA_LINKEDIN_HABILITADA": valor})

        assert configuracao.linkedin_habilitado is True

    @pytest.mark.parametrize("valor", ["abc", "", "0", "-5", "1.5"])
    def test_usa_o_padrao_para_limites_invalidos(self, valor):
        configuracao = configuracao_leitura_vaga_do_ambiente(
            {"VAGA_LEITURA_LIMITE_POR_MINUTO": valor, "VAGA_LEITURA_LIMITE_POR_DIA": valor}
        )

        assert configuracao.limite_por_minuto == 10
        assert configuracao.limite_por_dia == 100

    @pytest.mark.parametrize("valor", ["abc", "", "0", "-1", "nan", "inf"])
    def test_usa_o_padrao_para_tempo_limite_invalido(self, valor):
        configuracao = configuracao_leitura_vaga_do_ambiente({"VAGA_LEITURA_TIMEOUT_SEGUNDOS": valor})

        assert configuracao.timeout_segundos == 15.0

import dataclasses

import pytest

from jobsync.vaga import DadosVaga


def _criar_dados(**overrides) -> DadosVaga:
    valores = dict(descricao="Descrição completa da vaga de Engenheiro de Software.")
    valores.update(overrides)
    return DadosVaga(**valores)


class TestDadosVaga:
    def test_cria_dados_com_apenas_a_descricao(self):
        dados = _criar_dados()

        assert dados.descricao == "Descrição completa da vaga de Engenheiro de Software."
        assert dados.cargo is None
        assert dados.empresa is None
        assert dados.local is None
        assert dados.url is None
        assert dados.tipo_contratacao is None
        assert dados.senioridade is None
        assert dados.setor is None

    def test_cria_dados_completos(self):
        dados = _criar_dados(
            cargo="Engenheiro de Software",
            empresa="Barte",
            local="Brasil",
            url="https://www.linkedin.com/jobs/view/4484559483/",
            tipo_contratacao="Tempo integral",
            senioridade="Sênior",
            setor="Serviços financeiros",
        )

        assert dados.cargo == "Engenheiro de Software"
        assert dados.empresa == "Barte"
        assert dados.local == "Brasil"
        assert dados.tipo_contratacao == "Tempo integral"

    def test_remove_espacos_das_pontas_dos_campos(self):
        dados = _criar_dados(cargo="  Engenheiro  ", empresa=" Barte ", descricao="  texto  ")

        assert dados.cargo == "Engenheiro"
        assert dados.empresa == "Barte"
        assert dados.descricao == "texto"

    def test_converte_campos_opcionais_em_branco_para_none(self):
        dados = _criar_dados(cargo="   ", empresa="", local=None)

        assert dados.cargo is None
        assert dados.empresa is None
        assert dados.local is None

    @pytest.mark.parametrize("descricao", ["", "   ", "\n\t"])
    def test_descricao_vazia_gera_erro(self, descricao):
        with pytest.raises(ValueError):
            _criar_dados(descricao=descricao)

    def test_descricao_acima_do_limite_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_dados(descricao="a" * 50_001)

    def test_cargo_acima_do_limite_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_dados(cargo="a" * 201)

    def test_dados_sao_imutaveis(self):
        dados = _criar_dados()

        with pytest.raises(dataclasses.FrozenInstanceError):
            dados.cargo = "Outro"

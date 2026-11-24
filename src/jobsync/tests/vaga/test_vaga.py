"""Testes da entidade de domínio Vaga."""

from datetime import datetime

import pytest

from jobsync.vaga import Vaga


def _criar_vaga(**overrides) -> Vaga:
    dados = dict(
        id="uuid-1",
        perfil_identificador="matheus",
        texto_descricao="Vaga para Engenheiro de Software Backend",
        data_captura=datetime(2026, 7, 26),
        url_origem="https://exemplo.com/vaga/123",
    )
    dados.update(overrides)
    return Vaga(**dados)


class TestVaga:
    def test_cria_vaga_valida(self):
        vaga = _criar_vaga()

        assert vaga.perfil_identificador == "matheus"
        assert vaga.url_origem == "https://exemplo.com/vaga/123"

    def test_url_origem_e_opcional(self):
        vaga = _criar_vaga(url_origem=None)

        assert vaga.url_origem is None

    def test_id_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_vaga(id="")

    def test_perfil_identificador_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_vaga(perfil_identificador="")

    def test_texto_descricao_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_vaga(texto_descricao="   ")

    def test_dados_extraidos_sao_opcionais(self):
        vaga = _criar_vaga()

        assert vaga.cargo is None
        assert vaga.empresa is None
        assert vaga.local is None

    def test_guarda_cargo_empresa_e_local(self):
        vaga = _criar_vaga(cargo="Engenheiro de Software", empresa="Barte", local="Brasil")

        assert vaga.cargo == "Engenheiro de Software"
        assert vaga.empresa == "Barte"
        assert vaga.local == "Brasil"

    def test_remove_espacos_e_converte_campos_em_branco_para_none(self):
        vaga = _criar_vaga(cargo="  Engenheiro  ", empresa="   ", local="")

        assert vaga.cargo == "Engenheiro"
        assert vaga.empresa is None
        assert vaga.local is None

    @pytest.mark.parametrize("campo", ["cargo", "empresa", "local"])
    def test_campo_acima_do_limite_de_tamanho_gera_erro(self, campo):
        with pytest.raises(ValueError):
            _criar_vaga(**{campo: "a" * 201})

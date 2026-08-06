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

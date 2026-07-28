"""Testes da entidade de domínio CurriculoSalvo."""

from datetime import datetime

import pytest

from domain.curriculo_salvo import CurriculoSalvo


def _criar_curriculo_salvo(**overrides):
    dados = dict(
        id="uuid-123",
        perfil_identificador="matheus",
        nome_referencia="Currículo Backend Sênior",
        pdf_bytes=b"%PDF-1.4 conteudo-fake",
        data_upload=datetime(2026, 7, 26, 12, 0, 0),
    )
    dados.update(overrides)
    return CurriculoSalvo(**dados)


class TestCurriculoSalvo:
    def test_cria_curriculo_salvo_valido(self):
        curriculo = _criar_curriculo_salvo()

        assert curriculo.nome_referencia == "Currículo Backend Sênior"
        assert curriculo.perfil_identificador == "matheus"

    def test_id_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_curriculo_salvo(id="")

    def test_perfil_identificador_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_curriculo_salvo(perfil_identificador="")

    def test_nome_referencia_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_curriculo_salvo(nome_referencia="")

    def test_pdf_bytes_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_curriculo_salvo(pdf_bytes=b"")

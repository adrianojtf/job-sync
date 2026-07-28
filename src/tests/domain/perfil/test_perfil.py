"""Testes da entidade de domínio Perfil."""

import pytest

from domain.perfil import Perfil


class TestPerfil:
    def test_cria_perfil_com_identificador_valido(self):
        perfil = Perfil(identificador="matheus")

        assert perfil.identificador == "matheus"

    def test_identificador_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            Perfil(identificador="")

    def test_identificador_apenas_espacos_gera_erro(self):
        with pytest.raises(ValueError):
            Perfil(identificador="   ")

    def test_perfil_e_imutavel(self):
        perfil = Perfil(identificador="matheus")

        with pytest.raises(Exception):
            perfil.identificador = "outro"

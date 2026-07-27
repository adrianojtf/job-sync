"""Testes do Value Object NomeArquivo.

Padrão exigido: nomeCompleto-data-cargoDoCandidato-empresa
"""
from datetime import date

import pytest

from domain.nome_arquivo import NomeArquivo


class TestNomeArquivo:
    def test_gera_nome_no_padrao_definido(self):
        nome = NomeArquivo.criar(
            nome_completo="Adriano João Teixeira Filho",
            cargo="Engenheiro de Software",
            empresa="Starian",
            data=date(2026, 7, 22),
        )

        assert nome.valor == "AdrianoJoaoTeixeiraFilho-2026-07-22-EngenheiroDeSoftware-Starian.pdf"

    def test_remove_acentos_e_caracteres_especiais(self):
        nome = NomeArquivo.criar(
            nome_completo="José da Silva Ção",
            cargo="Dev. Backend/Sênior",
            empresa="Empresa & Cia.",
            data=date(2026, 1, 5),
        )

        assert nome.valor == "JoseDaSilvaCao-2026-01-05-DevBackendSenior-EmpresaCia.pdf"

    def test_remove_espacos_duplicados_e_normaliza_camel_case(self):
        nome = NomeArquivo.criar(
            nome_completo="  Maria   Clara  ",
            cargo="Analista  de Sistemas",
            empresa="Tech   Solutions",
            data=date(2026, 3, 1),
        )

        assert nome.valor == "MariaClara-2026-03-01-AnalistaDeSistemas-TechSolutions.pdf"

    def test_nome_completo_vazio_gera_erro(self):
        with pytest.raises(ValueError, match="nome completo"):
            NomeArquivo.criar(
                nome_completo="",
                cargo="Dev",
                empresa="Empresa",
                data=date(2026, 1, 1),
            )

    def test_cargo_vazio_gera_erro(self):
        with pytest.raises(ValueError, match="cargo"):
            NomeArquivo.criar(
                nome_completo="Nome",
                cargo="   ",
                empresa="Empresa",
                data=date(2026, 1, 1),
            )

    def test_empresa_vazia_gera_erro(self):
        with pytest.raises(ValueError, match="empresa"):
            NomeArquivo.criar(
                nome_completo="Nome",
                cargo="Cargo",
                empresa="",
                data=date(2026, 1, 1),
            )

    def test_usa_data_atual_quando_nao_informada(self):
        nome = NomeArquivo.criar(
            nome_completo="Nome Sobrenome",
            cargo="Cargo",
            empresa="Empresa",
        )

        assert nome.valor.startswith("NomeSobrenome-")
        assert nome.valor.endswith("-Cargo-Empresa.pdf")

    def test_e_imutavel_value_object(self):
        nome = NomeArquivo.criar(
            nome_completo="Nome",
            cargo="Cargo",
            empresa="Empresa",
            data=date(2026, 1, 1),
        )
        with pytest.raises(AttributeError):
            nome.valor = "outro.pdf"

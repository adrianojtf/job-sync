"""Testes do caso de uso GerarPdfCurriculoRevisado."""
from datetime import date
from unittest.mock import Mock

import pytest

from jobsync.curriculo import (
    ExperienciaAdaptada,
    GeradorPdfPort,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.curriculo.service_layer.gerar_pdf_curriculo_revisado import (
    GerarPdfCurriculoRevisado,
    GerarPdfCurriculoRevisadoInputDto,
)


def _rascunho(nome_completo: str = "Ana Souza") -> RascunhoCurriculoAdaptado:
    return RascunhoCurriculoAdaptado(
        nome_completo=nome_completo,
        email="ana@ex.com",
        linkedin="",
        secoes=(SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Resumo revisado pelo usuário."),),
        experiencias=(
            ExperienciaAdaptada(
                cargo="Dev", empresa="TechCorp", periodo="2024", conquistas=("Texto editado.",)
            ),
        ),
    )


def _input_dto(**sobrescritas) -> GerarPdfCurriculoRevisadoInputDto:
    valores = {
        "rascunho": _rascunho(),
        "idioma_alvo": "pt",
        "cargo_alvo": "Engenheiro de Software",
        "empresa_alvo": "TechCorp",
        "data_referencia": date(2026, 11, 6),
    }
    valores.update(sobrescritas)
    return GerarPdfCurriculoRevisadoInputDto(**valores)


class TestGerarPdfCurriculoRevisado:
    def test_gera_pdf_a_partir_do_conteudo_revisado(self):
        gerador_pdf = Mock(spec=GeradorPdfPort)
        gerador_pdf.gerar.return_value = b"%PDF-revisado"
        rascunho = _rascunho()

        saida = GerarPdfCurriculoRevisado(gerador_pdf).executar(_input_dto(rascunho=rascunho))

        gerador_pdf.gerar.assert_called_once_with(rascunho.para_curriculo("pt"), "pt")
        assert saida.pdf_bytes == b"%PDF-revisado"

    def test_nome_do_arquivo_usa_o_nome_revisado(self):
        gerador_pdf = Mock(spec=GeradorPdfPort)
        gerador_pdf.gerar.return_value = b"%PDF"

        saida = GerarPdfCurriculoRevisado(gerador_pdf).executar(
            _input_dto(rascunho=_rascunho(nome_completo="Ana Corrigida"))
        )

        assert "AnaCorrigida" in saida.nome_arquivo.valor

    @pytest.mark.parametrize(
        ("campo", "valor", "mensagem"),
        [
            ("idioma_alvo", "es", "idioma"),
            ("cargo_alvo", " ", "cargo"),
            ("empresa_alvo", "", "empresa"),
        ],
    )
    def test_entrada_invalida_nao_gera_pdf(self, campo, valor, mensagem):
        gerador_pdf = Mock(spec=GeradorPdfPort)

        with pytest.raises(ValueError, match=mensagem):
            GerarPdfCurriculoRevisado(gerador_pdf).executar(_input_dto(**{campo: valor}))

        gerador_pdf.gerar.assert_not_called()
